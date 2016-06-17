# This file is called by autoexec.fxl which is run every time studio opens.
import FxStudio
import os.path


def oneTimeInit():
    runOnceFile = FxStudio.getConsoleVariable("g_userdirectory") + "Settings\\runonce"
    if os.path.exists(runOnceFile) == False:
        # This is the first time Studio has been run.
        if FxStudio.isCommandLineMode():
            FxStudio.warn('This appears to be FaceFX Studio\'s first run.')
            FxStudio.error('We still have a bit of set up left to do. Please run FaceFX Studio in normal (GUI) mode before running in command line mode.')
            FxStudio.setConsoleVariable('err_cli_init', '1')
        else:
            runOnceFileHandle = open(runOnceFile, "w")
            runOnceFileHandle.write("File to signal not to open intro content.")
            runOnceFileHandle.close()

            if FxStudio.displayYesNoBox("Would you be willing to help us make FaceFX Studio a better product? FaceFX Studio will prompt you to send a crash report in the event of a crash, but sometimes extra information goes a long way to helping our engineers track down an issue. In particularly rare or difficult to diagnose cases, it is helpful for our engineers to be able to contact you to discuss the issue. If you are willing to help, please answer yes to enter contact information to be sent along with crash reports.") == "yes":
                contactInfoFile = FxStudio.getConsoleVariable("g_userdirectory") + "Settings\\contact-info.txt"
                contactInfoPrompt = "Please enter your name and any contact information (email, phone, etc) on the single line below.\nThis information is stored in " + contactInfoFile + "\nand can be edited or removed at any time."
                contactInfo = FxStudio.getTextFromUser(contactInfoPrompt, "Contact Information")
                if len(contactInfo) > 0:
                    contactInfoFileHandle = open(contactInfoFile, "w")
                    contactInfoFileHandle.write(contactInfo)
                    contactInfoFileHandle.close()


def customizeFaceFX():
    try:
        # Note: PEP8 will list the following line as imported but unused but
        # this is intentional due to what this code is trying to do. Do not
        # remove this line.
        import facefxcustomize
    except ImportError:
        pass  # Ignore if facefxcustomize.py wasn't found.
    except Exception as e:
        FxStudio.error('Caught an exception while trying to import facefxcustomize.py: {0}'.format(str(e)))


if __name__ == '__main__':
    # Run any customization script the user provided.
    customizeFaceFX()

    # Perform one time initialization if required.
    oneTimeInit()

    # Start the plugin manager.
    try:
        import PluginManager
        PluginManager.initialize()
    except ImportError:
        FxStudio.error('The PluginManager or its UI were not found! Re-install FaceFX Studio to fix this problem.')
    except Exception as e:
        FxStudio.error('Caught an exception while trying to import PluginManager.py: {0}'.format(str(e)))
