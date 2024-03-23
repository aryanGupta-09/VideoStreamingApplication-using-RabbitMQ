import pika
import sys

class User:
    
    def __init__(self, username):
        self.username = username

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost')) # replace with youtube-server's ip
        # for remote server
        # credentials = pika.PlainCredentials('b', '1234')
        # self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
        
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.username)

    # subscribe or unsubscribe to a youtuber
    def update_subscription(self, youtuber, subscribe):
        body = f"{self.username} {'s' if subscribe else 'u'} {youtuber}"
        self.channel.basic_publish(exchange='', routing_key='user_requests', body=body)
        print("SUCCESS")

    # start receiving notifications
    def receive_notifications(self):
        def callback(ch, method, properties, body):
            print(f"New Notification: {body.decode()}")

        self.channel.basic_consume(queue=self.username, on_message_callback=callback, auto_ack=True)
        print("Waiting for notifications... press Ctrl+C to exit")
        self.channel.start_consuming()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        user = User(sys.argv[1])
        
        if sys.argv[2]=="s":
            user.update_subscription(sys.argv[3], True)
        elif sys.argv[2]=="u":
            user.update_subscription(sys.argv[3], False)
        else:
            print("Invalid Command")
    
    elif len(sys.argv) == 2:
        user = User(sys.argv[1])
        user.receive_notifications()
    
    else:
        print("Instructions:")
        print("1. For Subscription: python User.py <UserName> s <YouTuberName>")
        print("2. To Unsubscribe: python User.py <UserName> u <YouTuberName>")
        print("3. To start receiving Notifications: python User.py <UserName>")
