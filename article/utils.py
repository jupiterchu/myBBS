import pika

class RabbitMQ():
    def __init__(self,email):
        # 1、连接rabbitmq服务器

        credentials = pika.PlainCredentials('guest', 'rabbitmq')
        parameters = pika.ConnectionParameters(host='my_linux',
                                               port=5672,
                                               virtual_host='/',
                                               credentials=credentials)
        channel = pika.BlockingConnection(parameters)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='direct_demo', durable=False)

        # 2、创建一个名为hello的队列
        channel.queue_declare(queue='hello')
        # 3、简单模式,向名为hello队列中插入用户邮箱地址email
        channel.basic_publish(exchange='',
                              routing_key='hello',
                              body=email,
                              )


        print("发送用户邮箱：‘{}’ 到MQ成功".format(email))
        connection.close()