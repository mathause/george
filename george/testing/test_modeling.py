# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = [
    "test_constant_mean",
    "test_callable_mean",
    "test_gp_mean",
    "test_gp_white_noise",
    "test_gp_callable_mean",
]

import numpy as np

from ..gp import GP
from .. import kernels
from ..models import ConstantModel, CallableModel
from ..modeling import check_gradient, ModelingMixin


def test_constant_mean():
    m = ConstantModel(5.0)
    check_gradient(m, np.zeros(4))


def test_callable_mean():
    m = CallableModel(lambda x: 5.0 * x)
    check_gradient(m, np.zeros(4))


def test_gp_mean(N=50, seed=1234):
    np.random.seed(seed)
    x = np.random.uniform(0, 5)
    y = 5 + np.sin(x)
    gp = GP(10. * kernels.ExpSquaredKernel(1.3),
            mean=5.0, fit_mean=True)
    gp.compute(x)
    check_gradient(gp, y)


def test_gp_callable_mean(N=50, seed=1234):
    np.random.seed(seed)
    x = np.random.uniform(0, 5)
    y = 5 + np.sin(x)
    gp = GP(10. * kernels.ExpSquaredKernel(1.3),
            mean=lambda x: 5.0*x, fit_mean=True)
    gp.compute(x)
    check_gradient(gp, y)


def test_gp_white_noise(N=50, seed=1234):
    np.random.seed(seed)
    x = np.random.uniform(0, 5)
    y = 5 + np.sin(x)
    gp = GP(10. * kernels.ExpSquaredKernel(1.3),
            mean=5.0, fit_mean=True,
            white_noise=0.1, fit_white_noise=True)
    gp.compute(x)
    check_gradient(gp, y)


class LinearWhiteNoise(ModelingMixin):

    def __init__(self, m, b):
        super(LinearWhiteNoise, self).__init__(m=m, b=b)

    def get_value(self, x):
        m, b = self["m"], self["b"]
        return m * x + b

    @ModelingMixin.sort_gradient
    def get_gradient(self, x):
        return dict(m=x, b=np.ones(len(x)))


def test_gp_callable_white_noise(N=50, seed=1234):
    np.random.seed(seed)
    x = np.random.uniform(0, 5)
    y = 5 + np.sin(x)
    gp = GP(10. * kernels.ExpSquaredKernel(1.3), mean=5.0,
            white_noise=LinearWhiteNoise(-6, 0.01),
            fit_white_noise=True)
    gp.compute(x)
    check_gradient(gp, y)

    gp.freeze_parameter("white:m")
    check_gradient(gp, y)