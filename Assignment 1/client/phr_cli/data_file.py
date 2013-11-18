from phr_cli import protocol

import json

class DataFile(object):
    """
    Helper class to represent a data file. A data file contains information to
    interact with the PHR system. This class ensures the information stored and
    loaded on disk is of the right type.
    """

    class Meta:
        properties = [
            # API related
            ("host", basestring, None),
            ("categories", list, None),
            ("parties", list, None),
            ("mappings", dict, None),

            # Record related
            ("record_id", int, None),
            ("record_name", basestring, None),
            ("record_role", basestring, None),

            # Key related
            ("master_keys", dict, "key"),
            ("public_keys", dict, "key"),
            ("secret_keys", dict, "key")
        ]

    def __init__(self, data_file, load=False):
        """
        Initialize a new data file instance.

        @param data_file Output file name
        @param load Boolean to indicate if the load() method should be invoked
               directly
        """

        self.meta = self.Meta()
        self.protocol = None
        self.data_file = data_file

        # Directly load the data.
        if load:
            self.load()

    def get_protocol(self):
        """
        Helper method to instantiate a Protocol instance based on the properties
        categories, parties and mappings.

        @return Protocol instance
        @throws AttributeError if not all properties are available
        @throws ParameterError if properties are invalid
        """

        if self.protocol is None:
            self.protocol = protocol.Protocol(
                self.categories, self.parties, self.mappings
            )

        return self.protocol

    def save(self):
        """
        Save a given data file to file based on the Meta's properties
        definition.

        @throws TypeError when a properties is not of the requested type
        @throws IOError when file cannot be saved
        """

        data = {}

        # Iterate over each property
        for attribute, clazz, convert in self.meta.properties:
            if attribute in self.__dict__:
                value = self.__dict__[attribute]

                # Check if data is of requested type
                if not isinstance(value, clazz):
                    raise TypeError("Unexpected data type %s for %s (expected %s)" % (type(value).__name__, attribute, clazz.__name__))

                # Convert if required
                if convert == "key":
                    value = self.get_protocol().keys_to_base64(value)

                # Store it
                data[attribute] = value

        # Save it
        json.dump(data, open(self.data_file, "w"))

    def load(self):
        """
        Load a given file into this instance, based on the Meta's properties
        definition.

        @throws TypeError when a properties is not of the requested type
        @throws IOError when file cannot be read
        """

        # Load it
        data = json.load(open(self.data_file, "r"))

        # Iterate over each property
        for attribute, clazz, convert in self.meta.properties:
            if attribute in data:
                value = data[attribute]

                # Convert if required
                if convert == "key":
                    value = self.get_protocol().base64_to_keys(value)

                # Check if data is of requested type
                if not isinstance(value, clazz):
                    raise TypeError("Unexpected data type %s for %s (expected %s)" % (type(value).__name__, attribute, clazz.__name__))

                # Store it
                self.__dict__[attribute] = value
