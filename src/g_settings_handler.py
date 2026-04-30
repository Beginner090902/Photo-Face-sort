from src.custom_logging import setup_logger
loger = setup_logger(__name__)

# Zentrale Konfigurationsdatei für die gesamte App
class AppConfig:
    def __init__(self):
        self.db_path:str = None 
        self.folder_path:str = None
        self.current_mode:str = "GPU"
        self.threads:int = 1
    
    def set_db_path(self, db_path):
        self.db_path = db_path
        loger.info(f"DB Pfad gesetzt: {db_path}")
    
    def get_db_path(self):
        loger.info(f"DB Pfad geschickt: {self.db_path}")
        return self.db_path

    def set_db_folder_path(self, folder_path):
        self.folder_path = folder_path
        loger.info(f"DB Pfad gesetzt: {folder_path}")
    
    def get_db_folder_path(self):
        loger.info(f"DB Pfad geschickt: {self.folder_path}")
        return self.folder_path
    
    def set_db_current_mode(self, current_mode):
        self.folder_path = current_mode
        loger.info(f"DB Pfad gesetzt: {self.current_mode}")
    
    def get_db_current_mode(self):
        loger.info(f"DB Pfad geschickt: {self.current_mode}")
        return self.current_mode
        
    def set_db_threads(self, threads):
        self.folder_path = threads
        loger.info(f"DB Pfad gesetzt: {self.threads}")
    
    def get_db_threads(self):
        loger.info(f"DB Pfad geschickt: {self.threads}")
        return self.threads
    

# Globale Instanz (Singleton)
app_config = AppConfig()