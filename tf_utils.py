import numpy as np
import tensorflow as tf

import config as c


def conv2d(input, name, kshape, strides=(1, 1, 1, 1), dtype=np.float32, padding="SAME"):
    with tf.name_scope(name):
        with tf.name_scope('w_'+name):

            W = tf.get_variable(name='w_'+name,
                                shape=kshape,
                                initializer=tf.contrib.layers.xavier_initializer(uniform=False),
                                dtype=dtype)

        with tf.name_scope('b_'+name):
            b = tf.get_variable(name='b_' + name,
                                shape=[kshape[3]],
                                initializer=tf.contrib.layers.xavier_initializer(uniform=False),
                                dtype=dtype)
        out = tf.nn.conv2d(input, W, strides=strides, padding=padding)
        out = tf.nn.bias_add(out, b)
        out = tf.nn.leaky_relu(out, alpha=0.2)
        return out


def conv2d_act(input, name, kernel, strides, num_filters, dtype=tf.float32, initializer="msar", act_type="leaky", padding="SAME"):
    with tf.name_scope(name):
        in_c = input.shape.as_list()[-1]
        if initializer == "msar":
            init = tf.contrib.layers.variance_scaling_initializer()
        elif initializer == "xavier":
            init = tf.contrib.layers.xavier_initializer(uniform=False)
        else:
            raise NotImplementedError
        with tf.name_scope('w_' + name):
            W = tf.get_variable(name='w_' + name,
                                shape=(kernel, kernel, in_c, num_filters),
                                initializer=init,
                                dtype=dtype)

        with tf.name_scope('b_' + name):
            b = tf.get_variable(name='b_' + name,
                                shape=[num_filters],
                                initializer=tf.zeros_initializer(),
                                dtype=dtype)
            out = tf.nn.conv2d(input, W, strides=(1, strides, strides, 1), padding=padding)
            out = tf.nn.bias_add(out, b)
        if act_type == "relu":
            out = tf.nn.relu(out)
        elif act_type == "leaky":
            out = tf.nn.leaky_relu(out, alpha=0.2)
        return out


def deconv2d(input, name, kshape, n_outputs, strides=(1, 1)):
    with tf.name_scope(name):
        out = tf.contrib.layers.conv2d_transpose(input,
                                                 num_outputs= n_outputs,
                                                 kernel_size=kshape,
                                                 stride=strides,
                                                 padding='SAME',
                                                 weights_initializer=tf.contrib.layers.xavier_initializer_conv2d(uniform=False),
                                                 biases_initializer=tf.contrib.layers.xavier_initializer(uniform=False),
                                                 activation_fn=tf.nn.relu)
        return out


def deconv2d_act(input, name, kernel, stride, num_filters, act_type="leaky",
                 initializer="msra", dtype=tf.float32, padding="SAME", use_bias=True):
    with tf.name_scope(name):
        input_size = input.shape.as_list()
        if len(input_size) == 5:
            input = tf.reshape(input, shape=(input_size[0] * input_size[1],
                                             input_size[2],
                                             input_size[3],
                                             input_size[4]))
        if initializer == "msra":
            init = tf.contrib.layers.variance_scaling_initializer(dtype=dtype)
        elif initializer == "xavier":
            init = tf.contrib.layers.xavier_initializer(uniform=False)
        else:
            raise NotImplementedError
        if act_type == "relu":
            act = tf.nn.relu
        elif act_type == "leaky":
            act = tf.nn.leaky_relu
        else:
            raise NotImplementedError

        with tf.name_scope('conv2d_transpos'):
            out = tf.layers.conv2d_transpose(input,
                                         filters=num_filters,
                                         kernel_size=(kernel, kernel),
                                         strides=(stride, stride),
                                         padding=padding,
                                         kernel_initializer=init,
                                         activation=act,
                                         use_bias=use_bias)
        return out


def maxpool2d(x,name,kshape=(1, 2, 2, 1), strides=(1, 2, 2, 1)):
    with tf.name_scope(name):
        out = tf.nn.max_pool(x,
                             ksize=kshape, #size of window
                             strides=strides,
                             padding='SAME')
        return out


def upsample(input, name, factor=(2, 2)):
    size = [int(input.shape[1] * factor[0]), int(input.shape[2] * factor[1])]
    with tf.name_scope(name):
        out = tf.image.resize_bilinear(input, size=size, align_corners=None, name=None)
        return out


def fullyConnected(input, name, output_size, dtype=np.float32):
    with tf.name_scope(name):
        input_size = input.shape[1:]
        input_size = int(np.prod(input_size))
        W = tf.get_variable(name='w_'+name,
                            shape=[input_size, output_size],
                            initializer=tf.contrib.layers.xavier_initializer(uniform=False),
                            dtype=dtype)
        b = tf.get_variable(name='b_'+name,
                            shape=[output_size],
                            initializer=tf.contrib.layers.xavier_initializer(uniform=False),
                            dtype=dtype)
        input = tf.reshape(input, [-1, input_size])
        out = tf.nn.relu(tf.add(tf.matmul(input, W), b))
        return out


def dropout(input, name, keep_rate):
    with tf.name_scope(name):
        out = tf.nn.dropout(input, keep_rate)
        return out


def weighted_l2(pred, gt):
    with tf.name_scope('weighted_l2'):
        weight = get_loss_weight_symbol(gt)
        l2 = weight * tf.square(pred - gt)
        l2 = tf.reduce_sum(l2)
    return l2


def get_loss_weight_symbol(data):
    balancing_weights = c.BALANCING_WEIGHTS
    thresholds = c.THRESHOLDS
    weights = tf.zeros_like(data)
    if c.USE_BALANCED_LOSS:
        for i in range(len(thresholds)):
            weights = weights + balancing_weights[i] * tf.to_float(data >= thresholds[i])
    return weights


def down_sampling(input, kshape, stride, num_filters, name, padding="SAME"):
    with tf.name_scope("down_sample"):
        input_size = input.shape.as_list()
        if len(input_size) == 5:
            input = tf.reshape(input, shape=(input_size[0]*input_size[1],
                                             input_size[2],
                                             input_size[3],
                                             input_size[4]))
        out = conv2d_act(input,
                        kernel=kshape,
                        strides=stride,
                        num_filters=num_filters,
                        padding=padding,
                        name=name)
        if len(input_size) == 5:
            out_size = out.shape.as_list()
            out = tf.reshape(out, shape=(input_size[0],
                                         input_size[1],
                                         out_size[-3],
                                         out_size[-2],
                                         out_size[-1]))
    return out


def up_sampling(input, kshape, stride, num_filter, name):
    with tf.name_scope("up_sample"):
        input_size = input.shape.as_list()
        if len(input_size) == 5:
            input = tf.reshape(input, shape=(input_size[0] * input_size[1],
                                             input_size[2],
                                             input_size[3],
                                             input_size[4]))
        out = deconv2d_act(input,
                            kernel=kshape,
                            stride=stride,
                            num_filters=num_filter,
                            name=name)

        if len(input_size) == 5:
            out_size = out.shape.as_list()
            out = tf.reshape(out, shape=(input_size[0],
                                         input_size[1],
                                         out_size[-3],
                                         out_size[-2],
                                         out_size[-1]))
    return out


if __name__ == '__main__':
    gt = np.random.rand(5,5) * 255
    gt = gt.astype(np.uint8)
    print(gt)
    print(get_loss_weight_symbol(gt))