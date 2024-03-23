import pika
import sys

class Youtuber:
    
    def __init__(self):
        
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost')) # replace with youtube-server's ip
        # for remote server
        # credentials = pika.PlainCredentials('b', '1234')
        # self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))

        self.channel = self.connection.channel()

    def publish_video(self, youtuber, video_name):
        message = f"{youtuber} uploaded {video_name}"
        self.channel.basic_publish(exchange='', routing_key='youtuber_requests', body=message)
        print("SUCCESS")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Instructions: python Youtuber.py <YouTuberName> <VideoName>")
    
    else:
        youtuber = Youtuber()
        youtuber.publish_video(sys.argv[1], ' '.join(sys.argv[2:]))
