@ECHO OFF
start/wait pnputil -i -a "%~dp0RST_PV_20.0.0.1035.4_SV2_Win10\Drivers\iaStorVD.inf"
start/wait pnputil -i -a "%~dp0RST_PV_20.0.0.1035.4_SV2_Win10\HsaComponent\iaStorHsaComponent.inf"
start/wait pnputil -i -a "%~dp0RST_PV_20.0.0.1035.4_SV2_Win10\HsaExtension\iaStorHsa_Ext.inf"
exit
