from util import *
import fastdeploy as fd
import os
import pytest

class CaseBase(object):

    #temp skip hrnet-w18
    cases = ["pp_liteseg"]

    def set_trt_info(self):
        pass

    def teardown_method(self):
        #print_log(["stderr.log", "stdout.log"], iden="after predict")
        pass
    
    def setup_class(self):
        self.model_name = self.util.model_name
        self.csv_save_path = self.util.csv_path
        self.pdiparams = os.path.join(self.util.model_path, "model.pdiparams")
        self.pdmodel = os.path.join(self.util.model_path, "model.pdmodel")
        self.yaml_file = os.path.join(self.util.model_path, "deploy.yaml")
        self.date_path = self.util.data_path
        self.option = fd.RuntimeOption()
        self.option.enable_paddle_log_info()
        self.diff = 1e-5
        

    def run_predict(self):
        model = fd.vision.segmentation.PaddleSegModel(self.pdmodel, self.pdiparams, self.yaml_file, self.option)
        result = {}
        seg_result = fd.vision.evaluation.eval_segmentation(model, self.date_path)
        seg_result.pop("category_iou")
        result['miou'] = seg_result['miou']
        result['average_inference_time(s)'] = seg_result['average_inference_time(s)']
        print(result)
        return result

    @pytest.mark.skip(reason="PaddleSeg 暂时不支持ORT推理")
    def test_ort_cpu(self):
        self.option.use_ort_backend()
        self.option.use_cpu()
        result = self.run_predict()
        ret = check_result(result, self.util.ground_truth, "test_ort_cpu", self.model_name, self.diff, self.csv_save_path)

    @pytest.mark.skip(reason="PaddleSeg 暂时不支持ORT推理")
    def test_ort_gpu(self):
        self.option.use_ort_backend()
        self.option.use_gpu(0)
        result = self.run_predict()
        check_result(result, self.util.ground_truth, "test_ort_gpu", self.model_name, self.diff,self.csv_save_path)

    def test_paddle_cpu_backend(self):
        self.option.use_paddle_backend()
        self.option.use_cpu()
        result = self.run_predict()
        check_result(result, self.util.ground_truth, "test_paddle_cpu_backend", self.model_name, self.diff, self.csv_save_path)

    def test_paddle_gpu_backend(self):
        self.option.use_paddle_backend()
        self.option.use_gpu(0)
        result = self.run_predict()
        check_result(result, self.util.ground_truth, "test_paddle_gpu_backend", self.model_name, self.diff, self.csv_save_path)

    def test_trt(self):
        if self.model_name in CaseBase.cases:
            return
        self.set_trt_info()
        result = self.run_predict()
        check_result(result, self.util.ground_truth, "test_trt", self.model_name, self.diff, self.csv_save_path)


