class KafkaSearchException(Exception):
     def __init__(self, message="Custom exception"):
        self.message = message
        super().__init__(self.message)