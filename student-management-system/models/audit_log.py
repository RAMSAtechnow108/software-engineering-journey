class AuditLog:
    
    def __init__(self,log_id=None,action=None, create_at=None):
        self.log_id = log_id
        self.action = action
        self.created_at = create_at
        