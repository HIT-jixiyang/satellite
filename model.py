import os
import tensorflow as tf
import logging

from encoder import Encoder
from forecaster import Forecaster
from evaluation import get_loss_weight_symbol, \
    weighted_mse, weighted_mae, gdl_loss
import config as c


class Model(object):
    def __init__(self, restore_path=None, mode="train"):
        if c.DTYPE == "single":
            self._dtype = tf.float32
        elif c.DTYPE == "HALF":
            self._dtype = tf.float16
        self.mode=mode
        if mode == "train":
            self._batch = c.BATCH_SIZE
        else:
            self._batch = c.BATCH_SIZE

        self._in_seq = c.IN_SEQ
        if mode == "train":
            self._out_seq = c.OUT_SEQ
        else:
            self._out_seq = c.PREDICT_LENGTH
        if self.mode=='online':
            self._h = c.H_TEST
            self._w=c.W_TEST
        else:
            self._h = c.H_TRAIN
            self._w=c.W_TRAIN
        self._in_c = c.IN_CHANEL
        self.define_graph()
        tf_config = tf.ConfigProto(allow_soft_placement=True)
        tf_config.gpu_options.allow_growth = True
        self.sess = tf.Session(config=tf_config)
        writer = tf.summary.FileWriter("/extend/rain_data/Logs", self.sess.graph)
        self.saver = tf.train.Saver(max_to_keep=0)

        if restore_path is not None:
            self.saver.restore(self.sess, restore_path)

    def init_params(self):
        self.sess.run(tf.global_variables_initializer())

    def define_graph(self):
        with tf.variable_scope("Graph", reuse=tf.AUTO_REUSE):
            self.in_data_480 = tf.placeholder(self._dtype,
                                              shape=(self._batch, self._in_seq,
                                                 self._h, self._w, self._in_c),
                                              name="input")
            self.in_data_720 = tf.placeholder(self._dtype,
                                              shape=(self._batch, self._in_seq,
                                                 c.PRED_H, c.PRED_W, self._in_c),
                                              name="input2")
            self.gt_data_480 = tf.placeholder(self._dtype,
                                              shape=(self._batch, self._out_seq,
                                                     self._h, self._w, self._in_c),
                                              name="gt_480")
            self.gt_data_720 = tf.placeholder(self._dtype,
                                              shape=(self._batch, self._out_seq,
                                                     c.PRED_H, c.PRED_W, c.IN_CHANEL),
                                              name="gt_700")
            with tf.device('/device:GPU:0'):
                encoder_net = Encoder(self._batch, self._in_seq,mode=self.mode)
                if self.mode=='online':
                    encoder_net.stack_rnn_encoder(self.in_data_720)
                else:
                    encoder_net.stack_rnn_encoder(self.in_data_480)
            with tf.device('/device:GPU:1'):
                forecaster_net = Forecaster(self._batch, self._out_seq,mode=self.mode)
                forecaster_net.stack_rnn_forecaster(encoder_net.rnn_states)

            with tf.variable_scope("loss"):
                pred = forecaster_net.pred
                gt = self.gt_data_480
                with tf.name_scope('loss_weights'):
                    weights = get_loss_weight_symbol(pred)
                    self.result = pred
                if self.mode=='train':
                    self.mse = weighted_mse(pred, gt, weights)
                    self.mae = weighted_mae(pred, gt, weights)
                    self.gdl = gdl_loss(pred, gt)
                    loss = c.L1_LAMBDA * self.mse + c.L2_LAMBDA * self.mae + c.GDL_LAMBDA * self.gdl
                    self.optimizer = tf.train.AdamOptimizer(c.LR).minimize(loss)
                    self.mse_summary = tf.summary.scalar('mse', self.mse)
                    self.mae_summary = tf.summary.scalar('mae', self.mae)
                    self.gdl_summary = tf.summary.scalar('gdl', self.gdl)
                    self.merged = tf.summary.merge([self.mse_summary, self.mae_summary])
    def train_step(self, in_data, gt_data):
        _, merged,mse, mae, gdl, pred = self.sess.run([self.optimizer, self.merged,self.mse, self.mae, self.gdl, self.result],
                                               feed_dict={
                                                   self.in_data_480: in_data,
                                                   self.gt_data_480: gt_data
                                               })
        print("pred: ", pred.min(), pred.max())
        print("gt: ", gt_data.min(), gt_data.max())
        return mse, mae, gdl,merged

    def valid_step(self, in_data, gt_data):
        mse, mae, gdl, pred = self.sess.run([self.mse, self.mae, self.gdl, self.result],
                                            feed_dict={
                                                self.in_data_480: in_data,
                                                self.gt_data_480: gt_data
                                            })
        print("pred: ", pred.min(), pred.max())
        print("gt: ", gt_data.min(), gt_data.max())
        return mse, mae, gdl, pred

    def pred_step(self, in_data, gt_data=None):
        if in_data is not None:
            pred = self.sess.run(self.result,
                                 feed_dict={
                                     self.in_data_720: in_data
                                 })
            return pred
        else:
            return None
    def save_model(self, iter):
        from os.path import join
        save_path = self.saver.save(self.sess, join(c.SAVE_MODEL, "model.ckpt", str(iter)))
        print("Model saved in path: %s" % save_path)
