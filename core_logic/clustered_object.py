import random


class ClusteredObject:
    """
    Abstract object used for clustering by K-Means-Algorithm
    """

    def __init__(self, object_key, normalized_object_value, original_object_value):
        """
        single object for analysis with k-means,
        each object has unique "key" component, a (non-unique) normalized object value used for actual calculation and
        an original (non-unique) object value; each object has a centroid that it is currently mapped to (during
        initialization of object, this centroid is set as the normalized object value)
        :param object_key: unique key for each object to cluster
        :type object_key: no specific type needed, intended for use with string or tuple of integers
        :param normalized_object_value: object value plotted to normalized float
        :type normalized_object_value: Float from interval [0, 1]
        :param original_object_value: object value before normalization
        :type original_object_value: Integer
        """
        self.object_key = object_key
        self.normalized_object_value = normalized_object_value
        self.centroid = normalized_object_value
        self.original_object_value = original_object_value

    def __str__(self):
        return "Object: {objkey} - Value: {objvle} - Centroid: {ctrd}"\
            .format(objkey=self.object_key, objvle=self.original_object_value, ctrd=self.centroid)

    def get_object_key(self):
        """
        :return: key of object
        """
        return self.object_key

    def get_object_value(self):
        """
        :return: normalized object value as float in interval [0, 1]
        """
        return self.normalized_object_value

    def get_centroid(self):
        """
        :return: current centroid of this object as float in interval [0, 1]
        """
        return self.centroid

    def get_original_object_value(self):
        """
        :return: original value of object as integer
        """
        return self.original_object_value

    def set_centroid(self, new_centroid):
        """
        :param new_centroid: the new centroid of this object
        :type new_centroid: Float (should be in interval [0, 1])
        """
        self.centroid = new_centroid

    def reset_centroid(self, max_value):
        """
        used to reset the value of self.centroid during k-means
        :param max_value: if 0 resets itself to initial (normalized) value of given object, else it is assumed
        max_value is the maximum possible value for this k-mean calculation, the centroid is therefore reset to a
        random value, normalized in proportion to the given max_value (i.e. same normalization method as during
        initialisation of k-means is used, the centroid is therefore reset to a random position that could have also
        occurred during instantiation of the k-means-algorithm)
        :type max_value: Integer
        """
        if max_value == 0:
            self.centroid = self.normalized_object_value
        else:
            self.centroid = random.randint(1, max_value+1)/max_value

    @staticmethod
    def compare_objects(first_object, second_object):
        """
        :param first_object: first object for comparison
        :type first_object: ClusteredObject
        :param second_object: second object for comparison
        :type second_object: ClusteredObject
        :return True if keys, values and centroids of both objects are equal, False otherwise
        """
        if first_object.get_object_key() != second_object.get_object_key():
            return False
        elif first_object.get_object_value() != second_object.get_object_value():
            return False
        elif first_object.get_centroid() != second_object.get_centroid():
            return False
        return True

    @staticmethod
    def sort_objects_by_key(object_list):
        """
        returns new list() of objects via method copy_object_list()
        :param object_list: given object to sort
        :type object_list: List
        :return: a copy of the given list sorted by value of the key-parameter of each object in descending order
        """
        new_object_list = ClusteredObject.copy_object_list(object_list)
        new_object_list.sort(key=lambda x: x.object_key, reverse=True)
        return new_object_list

    @staticmethod
    def copy_object_list(given_list):
        """
        :param given_list: an object list to copy
        :type given_list: List
        :return: returns deep-copy of given object_list
        """
        new_object_list = list()
        for object_to_copy in given_list:
            new_object_list.append(ClusteredObject(object_to_copy.get_object_key(), object_to_copy.get_object_value(),
                                                   object_to_copy.get_original_object_value()))
        return new_object_list

