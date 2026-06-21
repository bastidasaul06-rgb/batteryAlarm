import globalPluginHandler
import ui
import wx
import tones
import config
import gui
import ctypes
import addonHandler
from ctypes import wintypes
from scriptHandler import script

addonHandler.initTranslation()


class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", wintypes.BYTE),
        ("BatteryFlag", wintypes.BYTE),
        ("BatteryLifePercent", wintypes.BYTE),
        ("Reserved1", wintypes.BYTE),
        ("BatteryLifeTime", wintypes.DWORD),
        ("BatteryFullLifeTime", wintypes.DWORD),
    ]


confspec = {
    "enabled": "boolean(default=True)",
    "threshold": "integer(default=20)",
    "chargeEnabled": "boolean(default=False)",
    "chargeThreshold": "integer(default=90)",
    "beepFrequency": "integer(default=880)",
    "beepDuration": "integer(default=500)",
    "checkInterval": "integer(default=5)",
}
config.conf.spec["batteryAlarm"] = confspec


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = "Bateria"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._alarming = False
        self._dismissed = False
        self._chargeAlarming = False
        self._chargeDismissed = False
        self._timer = wx.PyTimer(self._checkBattery)
        self._menuItem = None
        interval = config.conf["batteryAlarm"]["checkInterval"] * 1000
        self._timer.Start(interval)
        self._createMenu()

    def _getBatteryPercent(self):
        try:
            sps = SYSTEM_POWER_STATUS()
            ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(sps))
            if sps.BatteryLifePercent == 255:
                return None
            return sps.BatteryLifePercent
        except Exception:
            return None

    def _getACStatus(self):
        try:
            sps = SYSTEM_POWER_STATUS()
            ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(sps))
            return sps.ACLineStatus
        except Exception:
            return None

    def _checkBattery(self):
        percent = self._getBatteryPercent()
        ac = self._getACStatus()
        if percent is None:
            return
        conf = config.conf["batteryAlarm"]

        if not conf["enabled"]:
            self._alarming = False
            self._dismissed = False
            self._chargeAlarming = False
            self._chargeDismissed = False
            return

        dischargeThreshold = conf["threshold"]
        chargeEnabled = conf["chargeEnabled"]
        chargeThreshold = conf["chargeThreshold"]

        if ac != 0:
            # Charging
            # Reset discharge alarm
            if self._alarming or self._dismissed:
                self._alarming = False
                self._dismissed = False
                ui.message("Cargador conectado, alarma detenida")

            # Charge alarm logic
            if not chargeEnabled:
                self._chargeAlarming = False
                self._chargeDismissed = False
            elif percent >= chargeThreshold:
                if self._chargeDismissed:
                    pass
                else:
                    if not self._chargeAlarming:
                        self._chargeAlarming = True
                        ui.message(f"Carga completa: bateria al {percent}%")
                    self._playAlarm()
            else:
                if self._chargeAlarming or self._chargeDismissed:
                    self._chargeAlarming = False
                    self._chargeDismissed = False
                    ui.message(f"Bateria bajo umbral de carga, alarma detenida")
            return

        # Discharging
        if self._chargeAlarming or self._chargeDismissed:
            self._chargeAlarming = False
            self._chargeDismissed = False
            ui.message("Cargador desconectado, alarma de carga detenida")

        if percent > dischargeThreshold:
            if self._alarming or self._dismissed:
                self._alarming = False
                self._dismissed = False
                ui.message(f"Bateria subio al {percent}%, alarma detenida")
            return
        if self._dismissed:
            return
        if not self._alarming:
            self._alarming = True
            ui.message(f"Alarma: bateria al {percent}%")
        self._playAlarm()

    def _playAlarm(self):
        freq = config.conf["batteryAlarm"]["beepFrequency"]
        dur = config.conf["batteryAlarm"]["beepDuration"]
        tones.beep(freq, dur)

    def dismissAlarm(self):
        dismissed = False
        if self._alarming:
            self._alarming = False
            self._dismissed = True
            dismissed = True
        if self._chargeAlarming:
            self._chargeAlarming = False
            self._chargeDismissed = True
            dismissed = True
        if dismissed:
            ui.message("Alarma detenida por el usuario")

    def _createMenu(self):
        self._menuItem = gui.mainFrame.sysMenu.Append(
            wx.ID_ANY,
            "Alarma de Bateria - &Buscar actualizaciones...",
            "Buscar nuevas versiones del complemento en GitHub",
        )
        gui.mainFrame.sysMenu.Bind(wx.EVT_MENU, self._onUpdateMenu, self._menuItem)

    def _onUpdateMenu(self, event):
        self._checkForUpdates()

    def _getCurrentVersion(self):
        try:
            import addonHandler

            a = addonHandler.getCodeAddon()
            if a:
                return a.manifest["version"]
        except Exception:
            pass
        return "1.1.0"

    def _checkForUpdates(self):
        import urllib.request
        import json
        import os
        import tempfile

        try:
            req = urllib.request.Request(
                "https://api.github.com/repos/bastidasaul06-rgb/batteryAlarm/releases/latest",
                headers={"User-Agent": "batteryAlarm"},
            )
            resp = urllib.request.urlopen(req, timeout=10)
            release = json.loads(resp.read().decode())
            latest = release["tag_name"].lstrip("v")
            current = self._getCurrentVersion()
            if self._compareVersions(latest, current) <= 0:
                ui.message(f"No hay actualizaciones disponibles ({current})")
                return
            download = (
                release["assets"][0]["browser_download_url"]
                if release.get("assets")
                else ""
            )
            if not download:
                ui.message("Error: no se encontro archivo de descarga")
                return
            msg = (
                f"Version {latest} disponible (actual: {current}).\n"
                "Descargar e instalar la actualizacion?"
            )
            result = wx.MessageBox(
                msg,
                "Actualizacion disponible",
                wx.YES_NO | wx.ICON_QUESTION | wx.CENTER,
            )
            if result != wx.YES:
                return
            ui.message("Descargando actualizacion...")
            dlReq = urllib.request.Request(
                download, headers={"User-Agent": "batteryAlarm"}
            )
            dlResp = urllib.request.urlopen(dlReq, timeout=30)
            addonData = dlResp.read()
            tempPath = os.path.join(
                tempfile.gettempdir(), "batteryAlarm_update.nvda-addon"
            )
            with open(tempPath, "wb") as f:
                f.write(addonData)
            addonHandler.installAddonBundle(tempPath)
            try:
                os.remove(tempPath)
            except Exception:
                pass
            wx.MessageBox(
                "Actualizacion instalada correctamente.\n"
                "Reinicie NVDA para aplicar los cambios.",
                "Actualizacion completada",
                wx.OK | wx.ICON_INFORMATION | wx.CENTER,
            )
        except Exception as e:
            ui.message(f"Error al buscar actualizaciones: {e}")

    def _compareVersions(self, v1, v2):
        parts1 = [int(x) for x in v1.split(".")]
        parts2 = [int(x) for x in v2.split(".")]
        for a, b in zip(parts1, parts2):
            if a != b:
                return a - b
        return len(parts1) - len(parts2)

    @script(
        description="Buscar actualizaciones del complemento",
        category=scriptCategory,
        gesture="kb:NVDA+shift+alt+u",
    )
    def script_checkUpdates(self, gesture):
        wx.CallAfter(self._checkForUpdates)

    @script(
        description="Configurar alarma de bateria",
        category=scriptCategory,
        gesture="kb:NVDA+shift+alt+a",
    )
    def script_configBatteryAlarm(self, gesture):
        wx.CallAfter(self._showConfigDialog)

    @script(
        description="Detener alarma de bateria",
        category=scriptCategory,
        gesture="kb:NVDA+shift+alt+d",
    )
    def script_dismissBatteryAlarm(self, gesture):
        self.dismissAlarm()

    def _showConfigDialog(self):
        conf = config.conf["batteryAlarm"]

        dialog = wx.Dialog(None, title="Configuracion - Alarma de Bateria")
        panel = wx.Panel(dialog)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # -- Descarga --
        descLabel = wx.StaticText(panel, label="Alarma por descarga:")
        descLabel.SetFont(descLabel.GetFont().Bold())
        sizer.Add(descLabel, flag=wx.ALL, border=5)

        chk = wx.CheckBox(panel, label="&Activar alarma de descarga")
        chk.SetValue(conf["enabled"])
        sizer.Add(chk, flag=wx.ALL, border=5)

        hs = wx.BoxSizer(wx.HORIZONTAL)
        hs.Add(
            wx.StaticText(panel, label="&Umbral de descarga (%):"),
            flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL,
            border=5,
        )
        spin = wx.SpinCtrl(panel, min=1, max=100, initial=conf["threshold"])
        hs.Add(spin, flag=wx.ALL, border=5)
        sizer.Add(hs, flag=wx.EXPAND)

        # -- Carga --
        line = wx.StaticLine(panel)
        sizer.Add(line, flag=wx.EXPAND | wx.ALL, border=5)

        chargeLabel = wx.StaticText(panel, label="Alarma por carga completa:")
        chargeLabel.SetFont(chargeLabel.GetFont().Bold())
        sizer.Add(chargeLabel, flag=wx.ALL, border=5)

        chkCharge = wx.CheckBox(panel, label="Activar alarma de &carga")
        chkCharge.SetValue(conf["chargeEnabled"])
        sizer.Add(chkCharge, flag=wx.ALL, border=5)

        hsCharge = wx.BoxSizer(wx.HORIZONTAL)
        hsCharge.Add(
            wx.StaticText(panel, label="&Umbral de carga (%):"),
            flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL,
            border=5,
        )
        chargeSpin = wx.SpinCtrl(panel, min=1, max=100, initial=conf["chargeThreshold"])
        hsCharge.Add(chargeSpin, flag=wx.ALL, border=5)
        sizer.Add(hsCharge, flag=wx.EXPAND)

        # -- Sonido --
        line2 = wx.StaticLine(panel)
        sizer.Add(line2, flag=wx.EXPAND | wx.ALL, border=5)

        soundLabel = wx.StaticText(panel, label="Sonido:")
        soundLabel.SetFont(soundLabel.GetFont().Bold())
        sizer.Add(soundLabel, flag=wx.ALL, border=5)

        hs2 = wx.BoxSizer(wx.HORIZONTAL)
        hs2.Add(
            wx.StaticText(panel, label="Frecuencia (&Hz):"),
            flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL,
            border=5,
        )
        freqSpin = wx.SpinCtrl(panel, min=100, max=5000, initial=conf["beepFrequency"])
        hs2.Add(freqSpin, flag=wx.ALL, border=5)
        sizer.Add(hs2, flag=wx.EXPAND)

        hs3 = wx.BoxSizer(wx.HORIZONTAL)
        hs3.Add(
            wx.StaticText(panel, label="Duracion (&ms):"),
            flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL,
            border=5,
        )
        durSpin = wx.SpinCtrl(panel, min=50, max=5000, initial=conf["beepDuration"])
        hs3.Add(durSpin, flag=wx.ALL, border=5)
        sizer.Add(hs3, flag=wx.EXPAND)

        btnSizer = wx.StdDialogButtonSizer()
        testBtn = wx.Button(panel, label="&Probar sonido")
        btnSizer.Add(testBtn, flag=wx.ALL, border=5)
        btnSizer.Add(wx.Button(panel, wx.ID_OK), flag=wx.ALL, border=5)
        btnSizer.Add(wx.Button(panel, wx.ID_CANCEL), flag=wx.ALL, border=5)
        btnSizer.Realize()
        sizer.Add(btnSizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)

        testBtn.Bind(
            wx.EVT_BUTTON,
            lambda e: tones.beep(freqSpin.GetValue(), durSpin.GetValue()),
        )
        panel.SetSizer(sizer)
        sizer.Fit(dialog)
        dialog.CenterOnScreen()

        if dialog.ShowModal() == wx.ID_OK:
            conf["enabled"] = chk.GetValue()
            conf["threshold"] = spin.GetValue()
            conf["chargeEnabled"] = chkCharge.GetValue()
            conf["chargeThreshold"] = chargeSpin.GetValue()
            conf["beepFrequency"] = freqSpin.GetValue()
            conf["beepDuration"] = durSpin.GetValue()
            config.conf.save()
            interval = conf["checkInterval"] * 1000
            self._timer.Stop()
            self._timer.Start(interval)
            ui.message("Configuracion guardada")
        dialog.Destroy()

    def terminate(self):
        if self._timer:
            self._timer.Stop()
        try:
            gui.mainFrame.sysMenu.Remove(self._menuItem)
        except Exception:
            pass
        super().terminate()
