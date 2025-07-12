class AIServiceException(Exception):
   
   def __init__(self,message:str,original_error:Exception=None):
        super().__init__(message)
        self.original_error = original_error

class GeminiConnectionException(AIServiceException):
    """Exception raised for errors in connecting to the Gemini API."""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message, original_error)

class GeminiAPIException(AIServiceException):
    """Exception raised for errors returned by the Gemini API."""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message, original_error)

class InvalidPromptException(AIServiceException):
    """Exception raised for invalid prompts sent to the Gemini API."""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message, original_error)