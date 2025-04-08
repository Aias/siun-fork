import tensorflow as tf
# import keras.backend as K # No longer needed for session setting

def set_gpu_config(allow_growth=None, device_list='0'):
    """Configures GPU options for TensorFlow 2.x."""
    gpus = tf.config.list_physical_devices('GPU')
    if not gpus:
        print("No GPUs detected by TensorFlow.")
        return

    visible_gpus = []
    try:
        # Parse the device list string (e.g., '0,1')
        gpu_indices = [int(x) for x in device_list.split(',') if x.strip()]
        if not gpu_indices and gpus:
             # Default to the first GPU if list is empty/invalid but GPUs exist
             print("Warning: Empty or invalid device_list, defaulting to GPU 0.")
             gpu_indices = [0]

        for i in gpu_indices:
             if 0 <= i < len(gpus):
                  visible_gpus.append(gpus[i])
             else:
                  print(f"Warning: GPU index {i} out of range. Available GPUs: {len(gpus)}")

        if not visible_gpus and gpus:
            print("Warning: No valid GPUs selected from device_list, defaulting to GPU 0 if available.")
            # Attempt to default to GPU 0 if indices were invalid but GPUs exist
            if 0 < len(gpus):
                 visible_gpus = [gpus[0]]

        if not visible_gpus:
            print("Warning: No GPUs could be selected. Proceeding with CPU or default TF behavior.")
            # Set visible devices to empty list if truly no GPUs should be used
            tf.config.set_visible_devices([], 'GPU')
            return

        # Set only specified GPUs as visible
        tf.config.set_visible_devices(visible_gpus, 'GPU')
        print(f"Visible GPUs set to: {[gpu.name for gpu in visible_gpus]}")

        # Configure memory growth for visible GPUs
        if allow_growth is not None:
            for gpu in visible_gpus:
                tf.config.experimental.set_memory_growth(gpu, allow_growth)
                print(f"Memory growth set to {allow_growth} for {gpu.name}")

    except tf.errors.RuntimeError as e:
        # Visible devices and memory growth must be set before GPUs have been initialized
        print(f"Error setting GPU config (must be called at program start): {e}")
    except ValueError as e:
        print(f"Error parsing device_list '{device_list}': {e}")

# Original TF 1.x code commented out for reference
# def set_session_config(per_process_gpu_memory_fraction=None, allow_growth=None, device_list='0'):
#     """
#
#     :param allow_growth: When necessary, reserve memory
#     :param float per_process_gpu_memory_fraction: specify GPU memory usage as 0 to 1
#
#     :return:
#     """
#     import tensorflow as tf
#     import keras.backend as K
#
#     config = tf.ConfigProto(
#         gpu_options=tf.GPUOptions(
#             per_process_gpu_memory_fraction=per_process_gpu_memory_fraction,
#             allow_growth=allow_growth,
#             visible_device_list=device_list
#         )
#     )
#     sess = tf.Session(config=config)
#     K.set_session(sess)
