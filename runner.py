import logging
import os
import numpy as np

from model import Model
from iterator import Iterator
import config as c
from utils import config_log, save_png
from utils import normalize_frames, denormalize_frames
import tensorflow as tf
from supervisor.color_map import multi_process_transfer


class Runner(object):
    def __init__(self, para_tuple=None):

        self.para_tuple = para_tuple
        if para_tuple is None:
            self.model = Model()
        else:
            self.model = Model(restore_path=para_tuple[0], mode=para_tuple[1])
        if not para_tuple:
            self.model.init_params()

    def train(self):
        iter = 350000
        train_iter = Iterator(time_interval=c.RAINY_TRAIN,
                              sample_mode="random",
                              seq_len=c.IN_SEQ + c.OUT_SEQ)
        try:
            SummaryWriter = tf.train.SummaryWriter
        except:
            SummaryWriter = tf.summary.FileWriter
        writer = SummaryWriter(c.SAVE_SUMMARY, self.model.sess.graph)
        while iter < c.MAX_ITER:
            data, *_ = train_iter.sample(batch_size=c.BATCH_SIZE)
            in_data = data[:, :c.IN_SEQ, ...]
            gt_data = data[:, c.IN_SEQ:c.IN_SEQ + c.OUT_SEQ, ...]
            if c.NORMALIZE:
                in_data = normalize_frames(in_data)
                gt_data = normalize_frames(gt_data)

            mse, mae, gdl ,summary= self.model.train_step(in_data, gt_data)

            logging.info(f"Iter {iter}: \n\t mse:{mse} \n\t mae:{mae} \n\t gdl:{gdl}")
            # merged=self.model.sess.run(merged,feed_dict={self.model.in_data_480:in_data_480,self.model.gt_data_480:gt_data})
            writer.add_summary(summary,iter)
            if (iter + 1) % c.SAVE_ITER == 0:
                self.model.save_model(iter)

            if (iter + 1) % c.VALID_ITER == 0:
                self.run_benchmark(iter)
            # if (iter + 1) % c.TEST_ITER == 0:
            #         self.test(iter)
            iter += 1

    def run_benchmark(self, iter, mode="Valid"):
        if mode == "Valid":
            time_interval = c.RAINY_VALID
        else:
            time_interval = c.RAINY_TEST
        test_iter = Iterator(time_interval=time_interval,
                             sample_mode="sequent",
                             seq_len=c.IN_SEQ + c.OUT_SEQ,
                             stride=10, mode=mode)
        i = 1
        while not test_iter.use_up:

            data, date_clip, *_ = test_iter.sample(batch_size=c.BATCH_SIZE)

            data=np.array(data)
            if data.shape[0]==0:
                break
            print(data.shape)
            if mode == 'Valid':
                in_data = np.zeros(shape=(c.BATCH_SIZE, c.IN_SEQ, c.H_TRAIN, c.W_TRAIN, c.IN_CHANEL))
                gt_data = np.zeros(shape=(c.BATCH_SIZE, c.OUT_SEQ, c.H_TRAIN, c.W_TRAIN, c.IN_CHANEL))
                in_data[:, :, :, :, :] = data[:, :c.IN_SEQ, :, :, :]
                gt_data[:, :, :, :, :] = data[:, c.IN_SEQ:c.IN_SEQ + c.OUT_SEQ, :, :, :]
            else:
                in_data = np.zeros(shape=(c.BATCH_SIZE, c.DISPLAY_IN_SEQ, c.H_TEST, c.W_TEST, c.IN_CHANEL))
                gt_data = np.zeros(shape=(c.BATCH_SIZE, c.OUT_SEQ, c.H_TEST, c.W_TEST, c.IN_CHANEL))
                in_data[:, :, :, :, :] = data[:, :c.DISPLAY_IN_SEQ, :, :, :]
                gt_data[:, :, :, :, :] = data[:, c.DISPLAY_IN_SEQ:c.DISPLAY_IN_SEQ + c.OUT_SEQ, :, :, :]

            if type(data) == type([]):
                break

            if c.NORMALIZE:
                in_data = normalize_frames(in_data)
                gt_data = normalize_frames(gt_data)
            if mode == 'Valid':
                mse, mae, gdl, pred = self.model.valid_step(in_data, gt_data)
                logging.info(f"Iter {iter} {i}: \n\t mse:{mse} \n\t mae:{mae} \n\t gdl:{gdl}")
            else:
                pred = self.model.pred_step(in_data[:, 5:10])
            i += 1
            for b in range(c.BATCH_SIZE):
                predict_date = date_clip[b]
                logging.info(f"Save {predict_date} results")
                if mode == "Valid":
                    save_path = os.path.join(c.SAVE_VALID, str(iter), predict_date.strftime("%Y%m%d%H%M"))
                    display_path = os.path.join(c.SAVE_DISPLAY, str(iter), predict_date.strftime("%Y%m%d%H%M"))
                    save_in_data= in_data[b]
                    save_out_data = gt_data[b]
                    save_pred_data= pred[b]
                else:
                    display_path = os.path.join(c.SAVE_DISPLAY, str(iter), predict_date.strftime("%Y%m%d%H%M"))
                    save_path = os.path.join(c.SAVE_TEST, str(iter), predict_date.strftime("%Y%m%d%H%M"))
                    save_in_data = np.zeros((c.DISPLAY_IN_SEQ, 900, 900, 1))
                    save_out_data = np.zeros((c.OUT_SEQ, 900, 900, 1))
                    save_pred_data = np.zeros((c.PREDICT_LENGTH, 900, 900, 1))
                    save_in_data[:, 90:-90,:,:] = in_data[b]
                    save_out_data[:, 90:-90,:,:] = gt_data[b]
                    save_pred_data[:, 90:-90,:,:] = pred[b]

                path = os.path.join(save_path, "in")
                save_png(save_in_data, path)
                if mode!='Valid':
                    multi_process_transfer(path, display_path + '/in')

                path = os.path.join(save_path, "pred")
                save_png(save_pred_data, path)
                if mode != 'Valid':
                    os.system(r'./post_processing/postprocessing' + ' ' + save_path)
                    pred_display_dir = os.path.join(display_path, 'pred')
                    multi_process_transfer(path, pred_display_dir)
                # multi_process_transfer(path, display_path + 'pred')

                path = os.path.join(save_path, "out")
                save_png(save_out_data, path)
                if mode != 'Valid':
                    multi_process_transfer(path, display_path + '/out')

    def test(self,iter):
        iter = self.para_tuple[-1] + str(iter)+"_test"
        # self.model.mode="online"
        self.run_benchmark(iter, mode="online")


if __name__ == '__main__':
    config_log()
    paras = ('/extend/gru_tf_data/5_20_model/Save/model.ckpt/349999', "train")
    # paras = None
    runner = Runner(para_tuple=paras)
    runner.train()
    # runner.test('test-349999')
