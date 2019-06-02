import random
import math
from core_logic.various_errors import KMeanError
from core_logic.clustered_object import ClusteredObject


class KMeansHelper:
    """
    Helper class for clustering via K-Means-Algorithm
    """
    def __init__(self, given_objects, cluster_quantity):
        """
        uses list of objects of class ClusteredObject for clustering;
        normalizes input values to values between 0 and 1 (by dividing all values by the 10^x so that 10^x is greater or
        equal to all input values), initializes clusters with centres in range from 0 to 1
        :raises KMeanError if less objects then proposed clusters are given, or
        if all given_objects have less different possible clusters (by different values of given_objects) than proposed
        cluster quantity, or
        if at least one key (given at position [0] of each given_object) is used twice, or
        if negative values or values between 0 and 1 are input;
        :param given_objects: objects with (unique) key of each object at [0] (currently used with strings and tuples
        as "keys") and (non-unique) value of each object at [1]; expected value-input for each object in given_objects
        is positive integer >= 1 at position [1]
        :type given_objects: List
        :param cluster_quantity: proposed quantity of clusters
        :type cluster_quantity: Integer
        """
        if len(given_objects) < cluster_quantity:
            raise KMeanError(-1)
        list_of_given_values = list()
        list_of_given_keys = list()
        list_of_all_values = list()
        for single_object in given_objects:
            list_of_all_values.append(single_object[1])
            if single_object[1] not in list_of_given_values:
                list_of_given_values.append(single_object[1])
            if single_object[0] not in list_of_given_keys:
                list_of_given_keys.append(single_object[0])
        if len(list_of_given_values) < cluster_quantity:
            raise KMeanError(-2)
        if len(list_of_given_keys) < len(given_objects):
            raise KMeanError(-3)
        min_given_value = min(list_of_given_values)
        if min_given_value < 0:
            raise KMeanError(1)
        elif min_given_value < 1:
            raise KMeanError(2)
        max_given_value = max(list_of_given_values)
        self.max_value = pow(10, math.ceil(math.log(max_given_value, 10)))
        self.objects_to_cluster = list()
        for single_object in given_objects:
            self.objects_to_cluster.append(ClusteredObject(single_object[0], single_object[1] / self.max_value, single_object[1]))
        new_objects_to_cluster = ClusteredObject.sort_objects_by_key(self.objects_to_cluster)
        self.cluster_quantity = cluster_quantity
        self.cluster_centroids = list()
        for number in range(cluster_quantity):
            self.cluster_centroids.append(random.randint(1, self.max_value + 1) / self.max_value)
        self.cluster_centroids.sort()
        self.objects_to_cluster = new_objects_to_cluster
        self.centroids_to_mapped_objects = KMeansHelper.get_current_centroids_to_objects_mapping(self.objects_to_cluster)

    def __str__(self):
        string = "Objects for clustering:\n"
        if len(self.objects_to_cluster) > 0:
            for clustered_object in self.objects_to_cluster:
                string += "{clsfobj}\n".format(clsfobj=clustered_object)
        string += "Clustercentroids:\n"
        if len(self.cluster_centroids) > 0:
            for centroids in self.cluster_centroids:
                string += "{ctrd} ; ".format(ctrd=centroids)
            string = string[:-2]
            string += "\n"
        string += "Mapping:\n"
        if len(self.centroids_to_mapped_objects.keys()) > 0:
            for centroid_key in self.centroids_to_mapped_objects.keys():
                string += "Key: {ctrdky} ".format(ctrdky=centroid_key)
                string += "Mapped objects:\n"
                for cluster_value in self.centroids_to_mapped_objects[centroid_key]:
                    string += "Object: {objct} - Value: {vle} | "\
                        .format(objct=cluster_value.get_object_key(), vle=cluster_value.get_original_object_value())
                string = string[:-2]
                string += "\n"
        return string

    def get_centroid_to_mapped_objects(self):
        """
        intended to check and return result after (iteration of) clustering
        :return: dict () of cluster centroids as keys and each object in cluster as values (i.e. values for each key is
        a list of objects of class ClusteredObject)
        """
        return self.centroids_to_mapped_objects

    def k_means(self, random_resetting=True):
        """
        main k-means-algorithm: initializes itself with current list of objects to cluster (intention: with initial
        list of objects to cluster) and current list of centroids (intention: with initial list of centroids);
        remaps all objects to a centroid (given by list of centroids); if centroids remain empty after remapping:
        reestablishes all lost centroids by creating new ones; recalculates new centroids from all elements of each
        cluster (again reestablishing lost clusters if necessary) | stops when no changes in the clustering occur
        :param random_resetting: used to distinguish between methods to reset cluster centroids, if true calls
        subroutine to re-establish cluster validity with max possible value for current k-mean calculation (saved during
        initialisation), if false calls this subroutine with value 0 instead
        :type random_resetting: Bool
        :return: None, upon completion sets dict() self.centroids_to_mapped_objects with clustering
        """
        objects_to_cluster_helper = ClusteredObject.copy_object_list(self.objects_to_cluster)
        cluster_centroid_helper = self.cluster_centroids.copy()
        while True:
            old_clustering = KMeansHelper.get_current_centroids_to_objects_mapping(objects_to_cluster_helper)
            objects_to_cluster_helper = KMeansHelper.map_instances_to_cluster_centroid(objects_to_cluster_helper,
                                                                                        cluster_centroid_helper)
            current_mapping = KMeansHelper.get_current_centroids_to_objects_mapping(objects_to_cluster_helper)
            if random_resetting:
                current_mapping = KMeansHelper.establish_cluster_validity(current_mapping, len(self.cluster_centroids),
                                                                          self.max_value)
            else:
                current_mapping = KMeansHelper.establish_cluster_validity(current_mapping, len(self.cluster_centroids),
                                                                          0)
            current_mapping = KMeansHelper.calculate_cluster_centroids(current_mapping)
            if random_resetting:
                current_mapping = KMeansHelper.establish_cluster_validity(current_mapping, len(self.cluster_centroids),
                                                                          self.max_value)
            else:
                current_mapping = KMeansHelper.establish_cluster_validity(current_mapping, len(self.cluster_centroids),
                                                                          0)
            cluster_centroid_helper = list(x for x in current_mapping.keys())
            objects_to_cluster_helper = list()
            for current_key in cluster_centroid_helper:
                new_objects = current_mapping[current_key]
                for single_object in new_objects:
                    objects_to_cluster_helper.append(single_object)
            new_clustering = KMeansHelper.get_current_centroids_to_objects_mapping(objects_to_cluster_helper)
            if KMeansHelper.compare_clustering(old_clustering, new_clustering):
                self.centroids_to_mapped_objects = new_clustering
                self.cluster_centroids = cluster_centroid_helper
                self.objects_to_cluster = objects_to_cluster_helper
                break

    @staticmethod
    def map_instances_to_cluster_centroid(object_list, centroid_list):
        """
        remaps all elements of given object list to their closest centroid given in centroid_list
        :param object_list: a list() of objects to remap
        :type object_list: List
        :param centroid_list: a list() of centroids to map objects to
        :type centroid_list: List
        :return: a new (copied) list() of objects with the centroid of each object set to the closest centroid of given
                 centroid_list
        """
        new_object_list = ClusteredObject.copy_object_list(object_list)
        for object_to_cluster in new_object_list:
            distances_to_cluster = list()
            for centroid in centroid_list:
                distances_to_cluster.append(abs(centroid - object_to_cluster.get_object_value()))
            new_centroid_index = distances_to_cluster.index(min(distances_to_cluster))
            new_centroid = centroid_list[new_centroid_index]
            object_to_cluster.set_centroid(new_centroid)
        return new_object_list

    @staticmethod
    def establish_cluster_validity(centroids_to_objects_mapping, centroid_quantity, max_value):
        """
        reestablishes n lost (empty) centroids by resetting centroids of n objects in centroids_to_objects_mapping (to
        their initial normalized object value or to a random value), objects that get their centroid reset are
        determined by distance of each object to their centroid (the n objects with the greatest distance are chosen),
        only one check for distance is made and all centroids are reset at once,
        :raise KMeansError if more centroids are in given centroids_objects_mapping then are given by quantity
        :param centroids_to_objects_mapping: dict() of centroid clusters as key and all objects they are mapped to
               as list() of values
        :type centroids_to_objects_mapping: Dictionary
        :param centroid_quantity: number of centroids that are supposed to be in the mapping
        :type centroid_quantity: Integer
        :param max_value: used to distinguish between different methods to reset cluster centroids, if max_value is not
        0, random reset will be used to determine new cluster centroid; if max_value is 0, reset via normalized object
        value will be used to determine new cluster centroid
        :type max_value: Integer
        :return: returns valid (regarding number of cluster centroids with at least one element) new mapping as dict()
                 of centroids as keys and all objects they are mapped to as values
        """
        invalid_centroid_quantity = centroid_quantity - len(centroids_to_objects_mapping.keys())
        if invalid_centroid_quantity < 0:
            raise KMeanError(0)
        if invalid_centroid_quantity > 0:
            value_distance_list = list()
            for current_key in centroids_to_objects_mapping.keys():
                for mapped_object in centroids_to_objects_mapping[current_key]:
                    value_distance_list.append([mapped_object,
                                                abs(mapped_object.get_object_value() - mapped_object.get_centroid())])
            value_distance_list.sort(key=lambda x: x[1], reverse=True)
            for invalid_centroid_index in range(invalid_centroid_quantity):
                value_distance_list[invalid_centroid_index][0].reset_centroid(max_value)
            new_object_list = list()
            for old_object in value_distance_list:
                new_object_list.append(old_object[0])
            new_centroid_to_object_mapping = KMeansHelper.get_current_centroids_to_objects_mapping(new_object_list)
            return new_centroid_to_object_mapping
        else:
            return centroids_to_objects_mapping

    @staticmethod
    def calculate_cluster_centroids(centroids_to_objects_mapping):
        """
        calculates new centroid value by dividing sum of all values in given cluster by size of cluster
        :param centroids_to_objects_mapping: dict() with centroids as keys and all objects in their cluster as values
        :type centroids_to_objects_mapping: Dictionary
        :return: a new dict() with recalculated centroids as keys and all objects in their cluster as values,
                 does NOT change arrangement of objects in cluster or reset their centroids
        """
        new_centroid_to_objects_mapping = dict()
        for current_cluster in centroids_to_objects_mapping.keys():
            values_in_cluster = list()
            objects_in_cluster = list()
            for single_object in centroids_to_objects_mapping[current_cluster]:
                values_in_cluster.append(single_object.get_object_value())
                objects_in_cluster.append(single_object)
            new_centroid = sum(values_in_cluster) / len(values_in_cluster)
            if new_centroid in new_centroid_to_objects_mapping.keys():
                old_objects_in_cluster = list(x for x in new_centroid_to_objects_mapping[new_centroid])
                objects_in_cluster.extend(old_objects_in_cluster)
            for new_object in objects_in_cluster:
                new_object.set_centroid(new_centroid)
            new_centroid_to_objects_mapping[new_centroid] = objects_in_cluster
        return new_centroid_to_objects_mapping

    @staticmethod
    def compare_clustering(clustering_1, clustering_2):
        """
        compares each centroid in both clusterings and each object in each cluster of both clusterings, comparison
        should be made between return values of the function get_centroid_to_mapped_objects()
        :param clustering_1: clustering as dict() for comparison
        :type clustering_1: Dictionary
        :param clustering_2: clustering as dict() for comparison
        :type clustering_2: Dictionary
        :return: True if all cluster centroids are identical and each cluster has the same objects (checked by key,
                 value and centroid of object), False otherwise
        """
        for old_key in clustering_1.keys():
            if old_key not in clustering_2.keys():
                return False
            old_objects = list(x for x in clustering_1[old_key])
            new_objects = list(x for x in clustering_2[old_key])
            for old_object in old_objects:
                contained_in_new = False
                for new_object in new_objects:
                    if ClusteredObject.compare_objects(old_object, new_object):
                        contained_in_new = True
                        break
                if not contained_in_new:
                    return False
        return True

    @staticmethod
    def get_current_centroids_to_objects_mapping(objects_to_cluster):
        """
        :param objects_to_cluster: list() of objects of class ClusteredObject used for the mapping
        :type objects_to_cluster: List
        :return: a dict() with each centroid occurring in at least one object (of given objects_to_cluster) as key,
                 values for each key are all objects (of class ClusteredObject) they occur in (i.e. value for each key
                 is a list of objects of class ClusteredObject)
        """
        current_mapping = dict()
        for clustered_object in objects_to_cluster:
            if clustered_object.get_centroid() not in current_mapping.keys():
                new_cluster = list()
                new_cluster.append(clustered_object)
                current_mapping[clustered_object.get_centroid()] = new_cluster
            else:
                new_cluster = list(x for x in current_mapping[clustered_object.get_centroid()])
                new_cluster.append(clustered_object)
                ClusteredObject.sort_objects_by_key(new_cluster)
                current_mapping[clustered_object.get_centroid()] = new_cluster
        cluster_as_key = list(x for x in current_mapping.keys())
        cluster_as_key.sort(reverse=True)
        sorted_mapping = dict()
        for cluster in cluster_as_key:
            sorted_values = list(x for x in current_mapping[cluster])
            ClusteredObject.sort_objects_by_key(sorted_values)
            sorted_mapping[cluster] = sorted_values
        return sorted_mapping

    @staticmethod
    def cluster_by_value(given_objects, cluster_quantity, max_tries, random_reset=False):
        """
        initialisation method for k-means-clustering, tries to create and cluster given objects with k-mean several
        times
        :raises KMeanError if no conclusive result is found (i.e. at least two out of all the tries are identical), or
        if an error occurs during initialisation
        :param given_objects: each containing a unique "key" (preferably as string or tuple) at position [0] and
        a non unique "value" (as int) at position [2]
        :type given_objects: List
        :param cluster_quantity: number of intended clusters
        :type cluster_quantity: Integer
        :param max_tries: indicates how many times the given_objects should be clustered via k-means, only the result
        that is identical to the most other results is output
        :param random_reset: used to specify which method of resetting cluster centroids during k-means should be used,
        if true uses random resetting, if false uses resetting by value, see function k_means for more information
        :type random_reset: Bool
        :return: a list with a conclusive k-means-analysis at position [0] and an integer indicating how many tries
        were identical to this result at position [1]
        """
        if (max_tries.__class__ is not int) | (max_tries <= 1):
            raise KMeanError(4)
        try:
            list_of_tries = list()
            while len(list_of_tries) < max_tries:
                new_k_mean_result = KMeansHelper(given_objects, cluster_quantity)
                new_k_mean_result.k_means(random_reset)
                list_of_tries.append(new_k_mean_result)
        except KMeanError as err:
            raise err
        else:
            best_result = None
            best_count = 0
            while len(list_of_tries) > 0:
                current_result = list_of_tries[0]
                current_count = 0
                list_of_tries.pop(0)
                for result in list_of_tries:
                    if KMeansHelper.compare_clustering(current_result.get_centroid_to_mapped_objects(),
                                                           result.get_centroid_to_mapped_objects()):
                        current_count += 1
                if current_count > best_count:
                    best_result = current_result
                    best_count = current_count
            if best_count > 0:
                return [best_result, best_count]
            else:
                raise KMeanError(3)
