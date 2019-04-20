import os
import pandas as pd
import numpy as np
import bisect

import config as cfg
from image import quick_read_frames, get_480x480_clip


class Iterator(object):
    """The iterator for the dataset

    """

    def __init__(self, time_interval, sample_mode, seq_len=30,
                 max_consecutive_missing=0, begin_ind=None, end_ind=None,
                 stride=None, width=None, height=None, base_freq='6min',mode='Train'):
        """Random sample: sample a random clip that will not violate the max_missing frame_num criteria
        Sequent sample: sample a clip from the beginning of the time.
                        Everytime, the clips from {T_begin, T_begin + 6min, ..., T_begin + (seq_len-1) * 6min} will be used
                        The begin datetime will move forward by adding stride: T_begin += 6min * stride
                        Once the clips violates the maximum missing number criteria, the starting
                         point will be moved to the next datetime that does not violate the missing_frame criteria

        Parameters
        ----------
        time_interval : list
            path of the saved pandas dataframe
        sample_mode : str
            Can be "random" or "sequent"
        seq_len : int
        max_consecutive_missing : int
            The maximum consecutive missing frames
        begin_ind : int
            Index of the begin frame
        end_ind : int
            Index of the end frame
        stride : int or None, optional
        width : int or None, optional
        height : int or None, optional
        base_freq : str, optional
        """
        assert isinstance(time_interval, list)
        self.time_interval = time_interval
        if width is None:
            width = cfg.W
        if height is None:
            height = cfg.H
        self.mode=mode
        self._df = self._df_generate()
        print("df size {}".format(self._df.size))

        self.set_begin_end(begin_ind=begin_ind, end_ind=end_ind)
        self._df_index_set = frozenset([self._df.index[i] for i in range(self._df.size)])
        self._seq_len = seq_len
        self._width = width
        self._height = height
        self._stride = stride
        self._max_consecutive_missing = max_consecutive_missing
        self._base_freq = base_freq
        self._base_time_delta = pd.Timedelta(base_freq)
        assert sample_mode in ["random", "sequent"], "Sample mode=%s is not supported" % sample_mode
        self.sample_mode = sample_mode
        if sample_mode == "sequent":
            assert self._stride is not None
            self._current_datetime = self.begin_time
            self._buffer_mult = 6
            self._buffer_datetime_keys = None
            self._buffer_frame_dat = None
            self._buffer_mask_dat = None
        else:
            self._max_buffer_length = None

    def set_begin_end(self, begin_ind=None, end_ind=None):
        self._begin_ind = 0 if begin_ind is None else begin_ind
        self._end_ind = self.total_frame_num - 1 if end_ind is None else end_ind

    @property
    def total_frame_num(self):
        return self._df.size

    @property
    def begin_time(self):
        return self._df.index[self._begin_ind]

    @property
    def end_time(self):
        return self._df.index[self._end_ind]

    @property
    def use_up(self):
        if self.sample_mode == "random":
            return False
        else:
            return self._current_datetime > self.end_time

    def _get_df(self):
        ref_path = cfg.REF_PATH
        refs = os.listdir(ref_path)
        refs = sorted(refs)
        date_list = []
        for file_ in refs:
            date = file_.split("_")[2]
            date = pd.to_datetime(date)
            date_list.append(date)
        df = pd.DataFrame([1 for i in range(len(date_list))],
                          columns=["rain"], index=date_list)
        return df

    def _df_generate(self):
        df = self._get_df()
        begin, end = self.time_interval
        begin = pd.to_datetime(begin)
        end = pd.to_datetime(end)
        date_list = []
        for date in df.index:
            if end >= date >= begin:
                date_list.append(date)
        new_df = pd.DataFrame([1 for i in range(len(date_list))],
                              columns=["rain"], index=date_list)
        return new_df

    def _next_exist_timestamp(self, timestamp):
        next_ind = bisect.bisect_right(self._df.index, timestamp)
        if next_ind >= self._df.size:
            return None
        else:
            return self._df.index[bisect.bisect_right(self._df.index, timestamp)]

    def _is_valid_clip(self, datetime_clip):
        """Check if the given datetime_clip is valid

        Parameters
        ----------
        datetime_clip :

        Returns
        -------
        ret : bool
        """
        missing_count = 0
        for i in range(len(datetime_clip)):
            if datetime_clip[i] not in self._df_index_set:
                return False
        return True

    def _load_frames(self, datetime_clips):
        assert isinstance(datetime_clips, list)
        for clip in datetime_clips:
            assert len(clip) == self._seq_len
        batch_size = len(datetime_clips)
        frame_dat = np.zeros((batch_size, self._seq_len, self._height, self._width, 1),
                             dtype=np.uint8)

        if self.sample_mode == "random":
            paths = []
            hit_inds = []
            miss_inds = []
            for i in range(self._seq_len):
                for j in range(batch_size):
                    timestamp = datetime_clips[j][i]
                    if timestamp in self._df_index_set:
                        paths.append(convert_datetime_to_filepath(datetime_clips[j][i]))
                        hit_inds.append([i, j])
                    else:
                        miss_inds.append([i, j])
            hit_inds = np.array(hit_inds, dtype=np.int)
            all_frame_dat = quick_read_frames(paths, self._height, self._width)
            frame_dat[hit_inds[:, 1], hit_inds[:, 0], :, :, :] = all_frame_dat
            # frame_dat=get_480x480_clip(frame_dat)
        else:
            # Get the first_timestamp and the last_timestamp in the datetime_clips
            first_timestamp = datetime_clips[-1][-1]
            last_timestamp = datetime_clips[0][0]
            for i in range(self._seq_len):
                for j in range(batch_size):
                    timestamp = datetime_clips[j][i]
                    if timestamp in self._df_index_set:
                        first_timestamp = min(first_timestamp, timestamp)
                        last_timestamp = max(last_timestamp, timestamp)
            if self._buffer_datetime_keys is None or \
                    not (first_timestamp in self._buffer_datetime_keys
                         and last_timestamp in self._buffer_datetime_keys):
                read_begin_ind = self._df.index.get_loc(first_timestamp)
                read_end_ind = self._df.index.get_loc(last_timestamp) + 1
                read_end_ind = min(read_begin_ind +
                                   self._buffer_mult * (read_end_ind - read_begin_ind),
                                   self._df.size)
                self._buffer_datetime_keys = self._df.index[read_begin_ind:read_end_ind]
                # Fill in the buffer
                paths = []
                for i in range(self._buffer_datetime_keys.size):
                    paths.append(convert_datetime_to_filepath(self._buffer_datetime_keys[i]))
                self._buffer_frame_dat = quick_read_frames(paths, self._height, self._width)
            for i in range(self._seq_len):
                for j in range(batch_size):
                    timestamp = datetime_clips[j][i]
                    if timestamp in self._df_index_set:
                        assert timestamp in self._buffer_datetime_keys
                        ind = self._buffer_datetime_keys.get_loc(timestamp)
                        frame_dat[j, i, :, :, :] = self._buffer_frame_dat[ind, :, :, :]
                        frame_dat = get_480x480_clip(frame_dat)
        return frame_dat

    def reset(self, begin_ind=None, end_ind=None):
        assert self.sample_mode == "sequent"
        self.set_begin_end(begin_ind=begin_ind, end_ind=end_ind)
        self._current_datetime = self.begin_time

    def random_reset(self):
        assert self.sample_mode == "sequent"
        self.set_begin_end(begin_ind=np.random.randint(0,
                                                       self.total_frame_num -
                                                       5 * self._seq_len),
                           end_ind=None)
        self._current_datetime = self.begin_time

    def check_new_start(self):
        assert self.sample_mode == "sequent"
        datetime_clip = pd.date_range(start=self._current_datetime,
                                      periods=self._seq_len,
                                      freq=self._base_freq)
        if self._is_valid_clip(datetime_clip):
            return self._current_datetime == self.begin_time
        else:
            return True

    def sample(self, batch_size, only_return_datetime=False):
        """Sample a minibatch from the sz radar ref dataset based on the given type and pd_file

        Parameters
        ----------
        batch_size : int
            Batch size
        only_return_datetime : bool
            Whether to only return the datetimes
        Returns
        -------
        frame_dat : np.ndarray
            Shape: (seq_len, valid_batch_size, 1, height, width)
        mask_dat : np.ndarray
            Shape: (seq_len, valid_batch_size, 1, height, width)
        date_time_clips : list
            length should be valid_batch_size
        new_start : bool
        """
        if self.sample_mode == 'sequent':
            if self.use_up:
                raise ValueError("The Iterator has been used up!")
            date_time_clips = []
            date_times = []
            new_start = False
            for i in range(batch_size):
                while not self.use_up:
                    datetime_clip = pd.date_range(end=self._current_datetime,
                                                  periods=self._seq_len,
                                                  freq=self._base_freq)

                    if self.is_valid_date(self._current_datetime):
                        new_start = new_start or (self._current_datetime == self.begin_time)
                        date_time_clips.append(datetime_clip)
                        date_times.append(self._current_datetime)
                        self._current_datetime += self._stride * self._base_time_delta
                        # self._current_datetime += self._base_time_delta
                        break
                    else:
                        new_start = True
                        self._current_datetime = \
                            self._next_exist_timestamp(timestamp=self._current_datetime)
                        if self._current_datetime is None:
                            # This indicates that there is no timestamp left,
                            # We point the current_datetime to be the next timestamp of self.end_time
                            self._current_datetime = self.end_time + self._base_time_delta
                            break
                        continue
            new_start = None if batch_size != 1 else new_start
            if only_return_datetime:
                return date_time_clips, new_start
            else:
                if self.use_up:
                    return [], []
                else:
                    if self.mode=='Train' or self.mode=='Valid':
                        frame_dat = self.get_crop(date_times,batch_size)
                    else:
                        frame_dat=self.get_test_data(date_times,batch_size)
                    return frame_dat, date_times, new_start, False

        else:
            assert only_return_datetime is False
            date_time_clips = []
            new_start = None
            date_times = []
            for i in range(batch_size):
                while True:
                    rand_ind = np.random.randint(0, self._df.size, 1)[0]
                    random_datetime = self._df.index[rand_ind]

                    if self.is_valid_date(random_datetime):
                        datetime_clip1 = pd.date_range(end=random_datetime,
                                                       periods=cfg.IN_SEQ,
                                                       freq=self._base_freq)
                        datetime_clip2 = pd.date_range(start=random_datetime,
                                                       periods=cfg.OUT_SEQ + 1,
                                                       freq=self._base_freq)
                        date_time_clip = []
                        date_time_clip[0:cfg.IN_SEQ] = datetime_clip1
                        date_time_clip[cfg.IN_SEQ:cfg.OUT_SEQ + cfg.IN_SEQ] = datetime_clip2[1:]
                        date_times.append(random_datetime)
                        date_time_clips.append(date_time_clip)
                        break
        if not date_times:
            return [], []
        frame_dat = self.get_crop(date_times,batch_size)
        return frame_dat, date_time_clips
    def get_test_data(self,datetimes,batch_size):
        # frame_dats=np.zeros(batch_size,cfg.IN_SEQ+cfg.OUT_SEQ,cfg.PRED_H,cfg.PRED_W,cfg.IN_CHANEL)
        frame_dats=[]
        for datetime in datetimes:
            print(datetime)
            datetime_clip1 = pd.date_range(end=datetime,
                                           periods=cfg.DISPLAY_IN_SEQ,
                                           freq=self._base_freq)
            datetime_clip2 = pd.date_range(start=datetime,
                                           periods=cfg.OUT_SEQ + 1,
                                           freq=self._base_freq)
            date_time_clip = []
            date_time_clip[0:cfg.DISPLAY_IN_SEQ] = datetime_clip1
            date_time_clip[cfg.DISPLAY_IN_SEQ:cfg.OUT_SEQ + cfg.DISPLAY_IN_SEQ] = datetime_clip2[1:]
            paths=[]
            for i in range(len(date_time_clip)):
                path=convert_datetime_to_filepath(date_time_clip[i])
                print('collect path: ---'+path)
                paths.append(path)
            try:
                frame_dat=quick_read_frames(paths,720,900)
            except IOError:
                continue
            frame_dats.append(frame_dat)
        frame_dats=np.array(frame_dats)
        # test_data=get_480x480_clip(clip=frame_dat,mode='pred')
        return frame_dats.reshape([batch_size,cfg.DISPLAY_IN_SEQ+cfg.OUT_SEQ,720,900,1])


    def is_valid_date(self, datetime):
        if self.mode!='online':
            dir = os.path.join(cfg.CROP_DATA_PATH, datetime.strftime("%Y%m%d%H%M"))
            if os.path.exists(dir):
                return True
            else:
                return False
        else:
            data_times_1=pd.date_range(end=datetime,periods=cfg.DISPLAY_IN_SEQ,freq=self._base_time_delta)
            for date in data_times_1:
                path=convert_datetime_to_filepath(date)
                if not os.path.exists(path):
                    return False
            data_times_2=pd.date_range(start=datetime,periods=cfg.OUT_SEQ+1,freq=self._base_time_delta)
            for date in data_times_2:
                path=convert_datetime_to_filepath(date)
                if not os.path.exists(path):
                    return False
            return True


    def get_crop(self, date_times,batch_size):
        """

        :param date_time:
        :return:(batch,seq_len,h,w,1)
        """
        assert date_times is not None
        frame_dat = np.zeros((batch_size, cfg.IN_SEQ + cfg.OUT_SEQ, cfg.H_TRAIN, cfg.W_TRAIN, 1),
                             dtype=np.uint8)
        for i in range(len(date_times)):
            in_dir = os.path.join(cfg.CROP_DATA_PATH, date_times[i].strftime("%Y%m%d%H%M"), 'in', '1')
            in_paths = [os.path.join(in_dir, str(i) + '.png') for i in range(1+cfg.IN_SEQ, 5+cfg.IN_SEQ +1)]

            out_dir = os.path.join(cfg.CROP_DATA_PATH, date_times[i].strftime("%Y%m%d%H%M"), 'out', '1')
            out_paths = [os.path.join(out_dir, str(i) + '.png') for i in range(1, cfg.OUT_SEQ + 1)]

            frame_dat[i, 0:cfg.IN_SEQ] = quick_read_frames(in_paths, cfg.H_TRAIN, cfg.W_TRAIN)
            frame_dat[i, cfg.IN_SEQ:cfg.OUT_SEQ + cfg.IN_SEQ] = quick_read_frames(out_paths, cfg.H_TRAIN, cfg.W_TRAIN)
        return frame_dat


def convert_datetime_to_filepath(date_time):
    """Convert datetime to the filepath

    Parameters
    ----------
    date_time : datetime.datetime

    Returns
    -------
    ret : str
    """
    # ret = os.path.join(cfg.REF_PATH, "cappi_ref_"+"%04d%02d%02d%02d%02d" %(
    #     date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute)
    #     +"_2500_0.ref")
    ret = os.path.join(cfg.REF_PATH, "cappi_ref_" + date_time.strftime("%Y%m%d%H%M")
                       + "_2500_0.png")
    return ret


if __name__ == '__main__':

    mode ='online'
    if mode == "Valid":
        time_interval = cfg.RAINY_VALID
    else:
        time_interval = cfg.RAINY_TEST
    test_iter = Iterator(time_interval=time_interval,
                         sample_mode="sequent",
                         seq_len=cfg.IN_SEQ + cfg.OUT_SEQ,
                         stride=10, mode=mode)
    i = 1
    while not test_iter.use_up:
        if i==2:
            break
        data, date_clip, *_ = test_iter.sample(batch_size=cfg.BATCH_SIZE)
        data = np.array(data)
        if data.shape[0] == 0:
            break
        print(data.shape)
        if mode == 'Valid':
            in_data = np.zeros(shape=(cfg.BATCH_SIZE, cfg.IN_SEQ, cfg.H_TRAIN, cfg.W_TRAIN, cfg.IN_CHANEL))
            gt_data = np.zeros(shape=(cfg.BATCH_SIZE, cfg.OUT_SEQ, cfg.H_TRAIN, cfg.W_TRAIN, cfg.IN_CHANEL))
            in_data[:, :, :, :, :] = data[:, :cfg.IN_SEQ, :, :, :]
            gt_data[:, :, :, :, :] = data[:, cfg.IN_SEQ:cfg.IN_SEQ + cfg.OUT_SEQ, :, :, :]
        else:
            in_data = np.zeros(shape=(cfg.BATCH_SIZE, cfg.DISPLAY_IN_SEQ, cfg.H_TEST, cfg.W_TEST, cfg.IN_CHANEL))
            gt_data = np.zeros(shape=(cfg.BATCH_SIZE, cfg.OUT_SEQ, cfg.H_TEST, cfg.W_TEST, cfg.IN_CHANEL))
            in_data[:, :, :, :, :] = data[:, :cfg.DISPLAY_IN_SEQ, :, :, :]
            gt_data[:, :, :, :, :] = data[:, cfg.DISPLAY_IN_SEQ:cfg.DISPLAY_IN_SEQ + cfg.OUT_SEQ, :, :, :]

        if type(data) == type([]):
            break
        iter='test-1'
        i += 1
        for b in range(cfg.BATCH_SIZE):
            predict_date = date_clip[b]
            if mode == "Valid":
                save_path = os.path.join(cfg.SAVE_VALID, str(iter), predict_date.strftime("%Y%m%d%H%M"))
                display_path = os.path.join(cfg.SAVE_DISPLAY, str(iter), predict_date.strftime("%Y%m%d%H%M"))
                save_in_data = in_data[0]
                save_out_data = gt_data[0]
            else:
                display_path = os.path.join(cfg.SAVE_DISPLAY, str(iter), predict_date.strftime("%Y%m%d%H%M"))
                save_path = os.path.join(cfg.SAVE_TEST, str(iter), predict_date.strftime("%Y%m%d%H%M"))
                save_in_data = np.zeros((cfg.DISPLAY_IN_SEQ, 900, 900, 1))
                save_out_data = np.zeros((cfg.OUT_SEQ, 900, 900, 1))
                save_pred_data = np.zeros((cfg.PREDICT_LENGTH, 900, 900, 1))
                save_in_data[:, 90:-90, :, :] = in_data[0]
                save_out_data[:, 90:-90, :, :] = gt_data[0]
            from utils import save_png
            from supervisor.color_map import multi_process_transfer
            path = os.path.join(save_path, "in")
            save_png(save_in_data, path)
            if mode != 'Valid':
                multi_process_transfer(path, display_path + '/in')
            # multi_process_transfer(path, display_path + 'pred')
            path = os.path.join(save_path, "out")
            save_png(save_out_data, path)
            if mode != 'Valid':
                multi_process_transfer(path, display_path + '/out')
    
