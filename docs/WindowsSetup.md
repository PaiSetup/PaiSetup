# Windows installation
- Before formatting old Windows:
  - Backup files onto external drive.
  - Download [media creation tool](https://www.microsoft.com/pl-pl/software-download/windows11) and create a pendrive with installation image. WARNING: it is incredibly difficult to do this from Linux. I tried multiple times and failed. Do **not** try, unless you have too much free time.
  - Clone *PaiSetup* and copy it to the pendrive.
- Install Windows 11.
- On new Windows:
  - Copy *PaiSetup* to desired directory (usually `D:\PaiSetup`).
  - Start and shutdown Edge. This is ridiculous, but some Powershell commands, which download stuff from internet depend on Edge. They need it to be started at least once. Fun.
  - Run `powershell.exe` as admin:
    ```
    Set-ExecutionPolicy Bypass
    D:\PaiSetup\pre_setup\windows.ps1
    python D:\PaiSetup\setup.py
    ```
  - Manual setup
    - MegaSync - exclude files for sync: Movies, TvSeries, Music, MusicToRate
    - ImageGlass - change what mouse wheel does, set as default image viewer
    - Notepad++ - Settings->Preferences->Language->Replace by Space
    - Browser - download location





# Chocolatey packages maintained by me for the sake of this project:
- [Microsoft PIX](https://community.chocolatey.org/packages/pix). Note: it is exempted from Chocolatey verification testing, because it must be performed on Windows Server 2012, which is not supported by Pix.
- [Xtreme Tuner](https://community.chocolatey.org/packages/xtreme-tuner).
- [Windows Handies](/steps/windows/packages/custom_packages/windows-handies). It is not hosted on Chocolatey servers, but used as a local package, because Windows Handies is my private little project that nobody will care about.





# To-do list:
- Chocolatey packages not working:
    - formatfactory
    - recuva
- Create Autohotkey scripts for installers, which do not give a way to select install path in CLI, but they do so in GUI:
    - Veracrypt
    - Fences3
    - Xtreme Tuner
    - Pix





# Useful links
- Silent Install HQ: https://silentinstallhq.com/
- Windows 10 Debloater: https://github.com/Sycnex/Windows10Debloater
- Chocolatey packages: https://community.chocolatey.org/packages
- Windows 10 – Useful Registry Paths for Apps & Settings https://eddiejackson.net/wp/?p=16373
- https://renenyffenegger.ch/notes/index.html
