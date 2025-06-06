import os
import tensorflow as tf
from tensorflow.keras.layers import *
from tensorflow.keras.initializers import glorot_uniform
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import LeakyReLU
from tensorflow.keras import backend as K

class DDModel:#Details Deblurring Model

    def __init__(self,config):
        self.config = config
        self.generator = self.build_generator((None,None,6),(None,None,3))

    def __resblock(self,X,filter_num):
        # Save the input value.
        X_shortcut = X
        
        X = Conv2D(filters = filter_num, kernel_size = (3, 3), strides = (1,1), padding = 'same')(X)
        X = Activation('relu')(X)
        
        X = Conv2D(filters = filter_num, kernel_size = (3, 3), strides = (1,1), padding = 'same')(X)
        X = Add()([X, X_shortcut])
        
        return X

    def __eblock(self,X,filter_num,stride):
        X = Conv2D(filters = filter_num, kernel_size = (5, 5), strides = (stride,stride), padding = 'same')(X)
        X = Activation('relu')(X)
        for i in range(3):
            X = self.__resblock(X,filter_num)
        return X

    def __dblock(self,X,filter_num,stride):
        for i in range(3):
            X = self.__resblock(X,filter_num*2)
        X = Conv2DTranspose(filter_num, kernel_size = (5, 5), strides = (stride, stride), padding='same')(X)
        X = Activation('relu')(X)
        return X

    def __outblock(self,X,filter_num):
        for i in range(3):
            X = self.__resblock(X,filter_num)
        X = Conv2D(3, kernel_size = (5, 5), strides = (1, 1), padding='same')(X)
        X = Activation('tanh')(X)
        X = Lambda(lambda x: x/2+0.5)(X)
        return X

    def __unet1(self,X):
        e32 = self.__eblock(X,32,1)#None,None,32
        e64 = self.__eblock(e32,64,2)#/2,64
        e128 = self.__eblock(e64,128,2)#/4,128
        d64 = self.__dblock(e128,64,2)#/2,64
        d64e64 = Add()([d64, e64])
        d32 = self.__dblock(d64e64,32,2)#None,None,32
        d32e32 = Add()([d32, e32])
        #d3 = self.__outblock(d32e32,32)
        return d32e32

    def __unet2(self,X):
        e32 = self.__eblock(X,32,1)#None,None,32
        e64 = self.__eblock(e32,64,2)#/2,64
        e128 = self.__eblock(e64,128,2)#/4,128
        d64 = self.__dblock(e128,64,2)#/2,64
        d64e64 = Add()([d64, e64])
        d32 = self.__dblock(d64e64,32,2)#None,None,32
        d32e32 = Add()([d32, e32])
        d3 = self.__outblock(d32e32,32)
        return d3

    def __makeDense(self,X,growthRate):
        out = Conv2D(filters = growthRate, kernel_size = (3, 3), strides = (1,1), padding = 'same', use_bias=False)(X)
        out = Activation('relu')(out)
        out = concatenate([X,out], axis=3)
        return out

    def __RDB(self,X,nChannels,nDenselayer,growthRate):
        X_shortcut = X
        for i in range(nDenselayer):    
            X = self.__makeDense(X, growthRate)
        X = Conv2D(filters = nChannels, kernel_size = (1, 1), strides = (1,1), padding = 'same', use_bias=False)(X)
        X = Add()([X, X_shortcut])
        return X

    def build_generator(self,input_shapeA,input_shapeB):#unet
        # if(self.load(self.config.resource.generator_json_path,self.config.resource.generator_weights_path)):
        #     return self.model
        # else:#init
        # Always build the model definition from code, then try loading weights later
        print(f'Building network architecture from code...')
        inputsA = Input(input_shapeA,name='imageSmall')#None,None,6
        inputsB = Input(input_shapeB,name='imageUp')#None,None,3
        #layer 1
        F_ = Conv2D(filters = 32, kernel_size = (3, 3), strides = (1,1), padding = 'same')(inputsA)#conv1
        F_0 = self.__unet1(F_)#32
        F_1 = self.__RDB(F_0,32,6,32)#RDB1
        F_2 = self.__RDB(F_1,32,6,32)#RDB2
        F_3 = self.__RDB(F_2,32,6,32)#RDB3
        FF = concatenate([F_1, F_2,F_3], axis=3)
        FdLF = Conv2D(filters = 32, kernel_size = (1, 1), strides = (1,1), padding = 'same')(FF)
        FGF = Conv2D(filters = 32, kernel_size = (3, 3), strides = (1,1), padding = 'same')(FdLF)
        FDF = Add()([FGF, F_])
        us = Conv2D(filters = 32*4, kernel_size = (3, 3), strides = (1,1), padding = 'same')(FDF)
        
        # Define output shape function for depth_to_space
        def depth_to_space_shape(input_shape):
            # input_shape = (batch, height, width, channels)
            if None in input_shape[1:3]: # If height or width are None
                return (input_shape[0], None, None, input_shape[3] // 4)
            else:
                 return (input_shape[0], input_shape[1] * 2, input_shape[2] * 2, input_shape[3] // 4)

        # us = Lambda(lambda x: tf.depth_to_space(x,2), output_shape=depth_to_space_shape)(us)#x2(upsample),32
        # Use tf.nn.depth_to_space for TF 2.x
        us = Lambda(lambda x: tf.nn.depth_to_space(x,2), output_shape=depth_to_space_shape)(us)#x2(upsample),32
        d3 = Conv2D(filters = 3, kernel_size = (3, 3), strides = (1,1), padding = 'same')(us)
        d3 = Activation('tanh')(d3)
        d3 = Lambda(lambda x: x/2+0.5)(d3)
        combined = concatenate([inputsB, d3], axis=3)#blur-generator,6
        o2 = self.__unet2(combined)
        model = Model(inputs=[inputsA,inputsB], outputs=o2, name='generator')

        # Attempt to load weights into the newly built model
        weights_path = self.config.resource.generator_weights_path
        if os.path.exists(weights_path):
            print(f'Loading weights from {weights_path}...')
            try:
                model.load_weights(weights_path)
                print("Loaded model weights from disk")
            except Exception as e:
                print(f"Error loading weights: {e}")
                print("Proceeding with initialized weights.")
        else:
            print(f"Weights file not found at {weights_path}. Using initialized weights.")

        return model

    # def load(self, json_path, weights_path):
    #     # from tensorflow.keras.models import model_from_json, Model # Import Model
    #     if os.path.exists(json_path) and os.path.exists(weights_path):
    #         # json_file = open(json_path, 'r')
    #         # loaded_model_json = json_file.read()
    #         # json_file.close()
    #         # Pass Model class in custom_objects
    #         # self.model = model_from_json(loaded_model_json,custom_objects={'tf':tf, 'Model': Model})
    #         # load weights into new model
    #         print(f"Loading weights from {weights_path}")
    #         self.model.load_weights(weights_path)
    #         print("Loaded model from disk")
    #         return True
    #     else:
    #         return False

    def save(self, model, json_path, weights_path):
        # serialize model to JSON - Deprecated for TF2/Keras3
        # model_json = model.to_json()
        # with open(json_path, "w") as json_file:
        #     json_file.write(model_json)
        # serialize weights to HDF5
        # Prefer saving the whole model in the new .keras format
        keras_path = weights_path.replace(".h5", ".keras")
        try:
            model.save(keras_path)
            print(f"Saved model to disk (new format): {keras_path}")
            # Optionally save weights separately if needed
            # model.save_weights(weights_path)
            # print(f"Saved weights to disk (HDF5): {weights_path}")
        except Exception as e:
            print(f"Error saving model: {e}")