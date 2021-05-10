from tensorflow import keras
from tensorflow.keras import backend as K


class Attention(keras.layers.Layer):

    def __init__(self, return_sequences=True):
        self.return_sequences = return_sequences
        super(Attention, self).__init__()

    def build(self, input_shape):
        self.W = self.add_weight(name="att_weight", shape=(input_shape[-1], 1),
                                 initializer="normal")
        self.b = self.add_weight(name="att_bias", shape=(input_shape[1], 1),
                                 initializer="zeros")

        super(Attention, self).build(input_shape)

    def call(self, x):
        e = K.tanh(K.dot(x, self.W) + self.b)
        a = K.softmax(e, axis=1)
        output = x * a

        if self.return_sequences:
            return output

        return K.sum(output, axis=1)

    def get_config(self):
        config = super().get_config().copy()
        config.update({
            'return_sequences': self.return_sequences,
        })
        return config

class Composer():
    def __init__(self, name, model_fp, network_input, network_input_shape, pitch_names, sequence_length, n_vocab):
        self.name = name
        self.model_fp = model_fp
        self.network_input = network_input
        self.network_input_shape = network_input_shape
        self.pitch_names = pitch_names
        self.sequence_length = sequence_length,
        self.n_vocab = n_vocab,
        self.model = None


    def init_model(self):
        """Initialize Composers' Model"""

        print("Initializing Model")
        print(f"N_vocab: {self.n_vocab}")

        self.model = keras.models.Sequential([
            keras.layers.LSTM(512, input_shape=(self.network_input_shape[1], self.network_input_shape[2]), return_sequences=True),
            keras.layers.Dropout(0.2),
            Attention(return_sequences=True),
            keras.layers.LSTM(512, return_sequences=True),
            keras.layers.Dropout(0.2),
            keras.layers.Flatten(input_shape=(self.sequence_length, 512)),
            keras.layers.Dense(256),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(self.n_vocab[0], activation='softmax'),
        ])

        self.model.compile(loss='categorical_crossentropy', optimizer='rmsprop')
        self.model.load_weights(self.model_fp)


    def get_model(self):
        return self.model

    def get_name(self):
        return self.name

    def get_network_input(self):
        return self.network_input

    def get_pitch_names(self):
        return self.pitch_names

    def get_n_vocab(self):
        return self.n_vocab