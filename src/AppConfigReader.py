import os
import sys
import logging

if getattr(sys, 'frozen', False):
    program_directory = os.path.dirname(os.path.abspath(sys.executable))
    ForceWriteLogToFile = True
else:
    program_directory = os.path.dirname(os.path.abspath(__file__))
    ForceWriteLogToFile = False
os.chdir(program_directory)

class AppConfigReader:
    """The AppConfigReader is a Module for PyYtDownloader-Remastered and actively refers itself using an Instance. It is based off of PyChat-Remastered's AppConfigReader."""

    COMMENT = """# This is your PyYtDownloader-Remastered app.config File\n# If you don't know what you're doing, please close this File immideatly and use the Settings Window.\n# If you know what you're doing, you should commit to the Repository! ;)\n#\n# https://github.com/iLollek/PyYtDownloader-Remastered"""

    def __init__(self, filename: str):
        self.filename = filename
        self.filepath = f'{os.getcwd()}\\SystemData\\{filename}'
        self.config = {}
        self.REQUIRED_KEYS = ["CustomOutputPath", "YouTubeCookiePath", "ColorTheme", "UseSFX", "UseProxy", "UseCookie", "ProxyHost", "ProxyPort", "ProxyUseCredentials", "ProxyCredentialsUser", "ProxyCredentialsPassword", "UseMP3Tags", "UseLastFMAPI", "LastFMAPIKey"]

    def VerifyIntegrity(self) -> bool:
        """Verifies Integrity of the app.config File by running all Checks at once.
        This Method also adds Missing Keys and their default values if it can.

        Returns:
            - Boolean Value: True if all Checks are True, False if at least one Check is False."""
        
        logging.info(f'Verifying Integrity of {self.filename} at {self.filepath}')

        # Run all checks and return True only if all are True
        if (self.CheckForSystemDataFolder() and
                self.CheckForAppConfigFile() and
                self.CheckContentOfAppConfigFile()):
            return True
        else:
            try:
                missing_keys = self.GetMissingKeysInAppConfig()
                self.AddMissingAppConfigKey(missing_keys)
                return True
            except Exception as e:
                logging.error(f'While trying to add the missing keys, the following exception occoured: {e}')
                return False

    def CheckForSystemDataFolder(self) -> bool:
        """Checks if a SystemData Folder is present
        
        Returns:
            - Boolean Value: True if a SystemData Folder exists, False otherwise"""
        
        return os.path.exists(f'{os.getcwd()}\\SystemData')
    
    def CheckForAppConfigFile(self) -> bool:
        """Checks if the Filename exists under the SystemData Folder
        
        Returns:
            - Boolean Value: True if the File exists under the SystemData Folder, False otherwise"""
        
        return os.path.exists(f'{os.getcwd()}\\SystemData\\{self.filename}')
    
    def CheckContentOfAppConfigFile(self) -> bool:
        """Checks if the Data inside of the App Config File is correct after the PYD Standard

        Returns:
            - Boolean Value: True if the Data is correct, False otherwise"""

        if not self.config:
            logging.warning('The config Dictionary is empty. Did you run ReadAppConfig() before running CheckContentOfAppConfigFile()?')
            return False
        
        missing_keys = [key for key in self.REQUIRED_KEYS if key not in self.config]
        if missing_keys:
            for key in missing_keys:
                logging.warning(f'Missing required key in config: {key}')
            return False

        for key in self.config.keys():
            if key not in self.REQUIRED_KEYS:
                logging.warning(f'Unrecognized Key in config: {key} (Value: {self.config[key]})')
        
        return True
    
    def GetMissingKeysInAppConfig(self) -> list[str]:
        """Gets all Missing, but required Keys and returns the Keys that are missing in the app.config File.
        
        Returns:
            - keys (list[str]): A list containing the Missing Keys as string."""
        
        return [key for key in self.REQUIRED_KEYS if key not in self.config]
    
    def AddMissingAppConfigKey(self, keys: list[str]) -> None:
        """Adds Missing Keys into the app.config File (appends them at the end) with default values.
        
        Args:
            - keys (list[str]): A list containing the Missing Keys as string. If no default value is found for the key, it will assign "None" to it."""
        
        for key in keys:
            logging.warning(f'Adding Default Value {self.GetConfigKeyValue(key)} for Missing Key {key}')
            self.config[key] = self.GetConfigKeyValue(key)
        self.WriteAppConfig()


    def ReadAppConfig(self):
        """Reads the app.config File from the System and Initializes it into a Dictionary in the Python Runtime"""

        self.config = {}
        with open(self.filepath, 'r') as f:
            for line in f:
                if '||' in line:
                    key, value = line.strip().split('||')
                    self.config[key.strip()] = value.strip()

    def GetConfigKeyValue(self, Key: str) -> str|bool:
        """Reads from the Config and returns the Value of the Key parameter
        
        Args:
            - Key (str): The Config Key you want the Value of
            
        Returns:
            - Value (str): The Value of the Key. If the Key's Value is malformed, wrong or doesn't exist, you will receive a Default Value along with a WARN in Logging. Alternatively, if the Key doesn't exist, you will receive None"""
        
        if Key in self.REQUIRED_KEYS:
            match Key:
                case "CustomOutputPath":
                    if self.config.get(Key, None) == "None":
                        self.SetAppConfigValue("CustomOutputPath", os.path.join(os.environ['USERPROFILE'], 'Desktop'))
                        self.WriteAppConfig()
                        return self.config.get(Key, os.path.join(os.environ['USERPROFILE'], 'Desktop'))
                    else:
                        return self.config.get(Key, os.path.join(os.environ['USERPROFILE'], 'Desktop'))
                case "YouTubeCookiePath":
                    return self.config.get(Key, None)
                case "ColorTheme":
                    return self.config.get(Key, "BlueTheme")
                case "UseSFX":
                    return self.config.get(Key, True)
                case "UseProxy":
                    return self.config.get(Key, "False")
                case "UseCookie":
                    return self.config.get(Key, "False")
                case "ProxyHost":
                    return self.config.get(Key, "public.proxy.net") # TODO: Change to a Public Proxy later
                case "ProxyPort":
                    return self.config.get(Key, "8080") # TODO: Change to a Public Proxy later
                case "UseMP3Tags":
                    return self.config.get(Key, True)
                case "UseLastFMAPI":
                    return self.config.get(Key, False)
                case "LastFMAPIKey":
                    return self.config.get(Key, "None")
        else:
            return self.config.get(Key, None) if Key in self.config.keys() else None
        
    def SetAppConfigValue(self, key: str, value: str):
        """Sets a Value from the app.config Dictionary in the Python Runtime. Modifies your config Object / Instance.
        
        Args:
            - key (str): The key that you want to modify
            - value (str): The Value of the key you want to modify"""
        
        try:
            logging.info(f'Setting {key} value to {value}')
            self.config[key] = value
            logging.info(f'Set {key} value to {value}')
        except Exception as e:
            logging.error(f'Error while setting Key {key} value to {value}: {e}')

    def WriteAppConfig(self):
        """Writes the Config you pass as the Argument back to the app.config File on the Disk and executes a ReadAppConfig() after to update. Modifies your running AppConfig Instance."""
        try:
            logging.info("Writing app.config to disk")
            with open(f'{os.getcwd()}\\SystemData\\app.config', "w") as f:
                f.write(AppConfigReader.COMMENT + "\n\n")
                for key in self.config.keys():
                    f.write(f'{key} || {self.config[key]}\n')
            logging.info("Write successful")
            self.ReadAppConfig()
        except Exception as e:
            logging.error(f'Error while writing app.config to disk: {e}')
        

        


        
if __name__ == "__main__":
    config = AppConfigReader("app.config")
    print(config.CheckForSystemDataFolder())
    print(config.CheckForAppConfigFile())

    config.ReadAppConfig()

    print(config.CheckContentOfAppConfigFile())

    missing_keys = config.GetMissingKeysInAppConfig()
    config.AddMissingAppConfigKey(missing_keys)