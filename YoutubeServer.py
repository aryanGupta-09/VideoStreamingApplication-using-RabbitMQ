import pika
import threading

class YouTubeServer:

    def __init__(self):
        self.thread_local = threading.local()
        self.subscriptions = {}  # dictionary, key is youtuber and value is list of subscribers

        channel = self.get_channel()
        channel.queue_declare(queue='youtuber_requests')
        channel.queue_declare(queue='user_requests')

    def get_connection(self):
        if not hasattr(self.thread_local, "connection"):
            self.thread_local.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost')) # replace with 0.0.0.0
        
        return self.thread_local.connection

    def get_channel(self):
        connection = self.get_connection()
        
        if not hasattr(self.thread_local, "channel"):
            self.thread_local.channel = connection.channel()
        
        return self.thread_local.channel

    def consume_user_requests(self):
        channel = self.get_channel()

        def callback(ch, method, properties, body):
            message = body.decode()

            # split the message into username, u/s and youtuber
            split_message = message.split(' ')
            if len(split_message) != 3:
                print("Invalid message format")
                return

            subscribe = None
            if split_message[1] == 's':
                subscribe = True
            elif split_message[1] == 'u':
                subscribe = False
            else:
                print("Invalid message format")
                return

            username = split_message[0]
            print(f"{username} logged in")
            youtuber = split_message[2]
            self.update_subscriptions(youtuber, username, subscribe)
        
        consumer_tag = 'user_consumer'
        channel.basic_consume(queue='user_requests', on_message_callback=callback, auto_ack=True, consumer_tag=consumer_tag)
        
        print('Waiting for user requests...')
        channel.start_consuming()

    def consume_youtuber_requests(self):
        channel = self.get_channel()

        def callback(ch, method, properties, body):
            print(f"{body.decode()}")
            youtuber = body.decode().split(' ')[0]
            video_name = body.decode().split(' uploaded ')[1]
            if youtuber not in self.subscriptions:
                self.subscriptions[youtuber] = []

            self.notify_users(youtuber, video_name)

        consumer_tag = 'youtuber_consumer'
        channel.basic_consume(queue='youtuber_requests', on_message_callback=callback, auto_ack=True, consumer_tag=consumer_tag)
        
        print('Waiting for youtuber requests...')
        channel.start_consuming()

    def notify_users(self, youtuber, video_name):
        channel = self.get_channel()

        subscribed_users = self.subscriptions.get(youtuber, [])
        
        # notify each subscribed user
        for user in subscribed_users:
            channel.basic_publish(exchange='', routing_key=user, body=f"{youtuber} uploaded {video_name}")
            print(f"Notification -> {user}: {youtuber} has uploaded {video_name}")

    def update_subscriptions(self, youtuber, username, subscribe):
        if youtuber not in self.subscriptions:
            print(f"{youtuber} doesnt exist")

        else:
            if subscribe:
                self.subscribe_user(username, youtuber)
            else:
                self.unsubscribe_user(username, youtuber)
    
    def subscribe_user(self, username, youtuber):
        if username not in self.subscriptions[youtuber]:
            self.subscriptions[youtuber].append(username)
            print(f"User {username} subscribed to {youtuber}")
        else:
            print(f"user {username} is already subscribed to {youtuber}")
    
    def unsubscribe_user(self, username, youtuber):
        if username in self.subscriptions[youtuber]:
            self.subscriptions[youtuber].remove(username)
            print(f"User {username} unsubscribed from {youtuber}")
        else:
            print(f"user {username} is not subscribed to {youtuber}")

if __name__ == "__main__":
    server = YouTubeServer()

    # create threads for user and youtuber requests
    user_thread = threading.Thread(target=server.consume_user_requests)
    youtuber_thread = threading.Thread(target=server.consume_youtuber_requests)

    user_thread.start()
    youtuber_thread.start()

    user_thread.join()
    youtuber_thread.join()
