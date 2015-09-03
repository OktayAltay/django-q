from django_q.conf import Conf
from django.core.cache import caches, InvalidCacheBackendError


class Broker(object):
    def __init__(self, list_key=Conf.PREFIX):
        self.connection = self.get_connection(list_key)
        self.list_key = list_key
        self.cache = self.get_cache()

    def enqueue(self, task):
        """
        Puts a task onto the queue
        :type task: str
        :return: task id
        """
        pass

    def dequeue(self):
        """
        Gets a task from the queue
        :return: tuple with task id and task message
        """
        pass

    def queue_size(self):
        """
        :return: the amount of tasks in the queue
        """
        pass

    def delete_queue(self):
        """
        Deletes the queue from the broker
        """
        pass

    def purge_queue(self):
        """
        Purges the queue of any tasks
        """
        pass

    def delete(self, task_id):
        """
        Deletes a task from the queue
        :param task_id: the id of the task
        """
        pass

    def acknowledge(self, task_id):
        """
        Acknowledges completion of the task and removes it from the queue.
        :param task_id: the id of the task
        """
        pass

    def ping(self):
        """
        Checks whether the broker connection is available
        :rtype: bool
        """
        pass

    def set_stat(self, key, value, timeout):
        """
        Saves a cluster statistic to the cache provider
        :type key: str
        :type value: str
        :type timeout: int
        """
        if not self.cache:
            return
        key_list = self.cache.get(Conf.Q_STAT, [])
        if key not in key_list:
            key_list.append(key)
        self.cache.set(Conf.Q_STAT, key_list)
        return self.cache.set(key, value, timeout)

    def get_stat(self, key):
        """
        Gets a cluster statistic from the cache provider
        :type key: str
        :return: a cluster Stat
        """
        if not self.cache:
            return
        return self.cache.get(key)

    def get_stats(self, pattern):
        """
        Returns a list of all cluster stats from the cache provider
        :type pattern: str
        :return: a list of Stats
        """
        if not self.cache:
            return
        key_list = self.cache.get(Conf.Q_STAT)
        if not key_list or len(key_list) == 0:
            return []
        stats = []
        for key in key_list:
            stat = self.cache.get(key)
            if stat:
                stats.append(stat)
            else:
                key_list.remove(key)
        self.cache.set(Conf.Q_STAT, key_list)
        return stats

    @staticmethod
    def get_cache():
        """
        Gets the current cache provider
        :return: a cache provider
        """
        try:
            return caches[Conf.CACHE]
        except InvalidCacheBackendError:
            return None

    @staticmethod
    def get_connection(list_key=Conf.PREFIX):
        """
        Gets a connection to the broker
        :param list_key: Optional queue name
        :return: a broker connection
        """
        return 0


def get_broker(list_key=Conf.PREFIX):
    """
    Gets the configured broker type
    :param list_key: optional queue name
    :type list_key: str
    :return:
    """
    if Conf.IRONMQ:
        from brokers import iron_mq
        return iron_mq.IronMQBroker(list_key=list_key)
    elif Conf.DISQUE_NODES:
        from brokers import disque
        return disque.Disque(list_key=list_key)
    elif Conf.SQS:
        from brokers import aws_sqs
        return aws_sqs.Sqs(list_key=list_key)
    # default to redis
    else:
        from brokers import redis_broker
        return redis_broker.Redis(list_key=list_key)
