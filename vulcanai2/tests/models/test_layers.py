"""The script to test all layers and SELU activation properties hold."""
import pytest
import math
import copy
from functools import reduce
import torch
from vulcanai2.models.layers import BaseUnit, ConvUnit, DenseUnit
from vulcanai2.models.utils import selu_weight_init_, selu_bias_init_
from vulcanai2.models.dnn import DenseNet
from vulcanai2.models.cnn import ConvNet
from torch.utils.data import TensorDataset, DataLoader


class TestBaseUnit:
    """To test BaseUnit layer."""

    @pytest.fixture
    def baseunit(self):
        """Make Base unit fixture."""
        return BaseUnit()


class TestDenseUnit:
    """To test DenseUnit layer."""

    @pytest.fixture
    def dense_unit(self):
        """Dense unit fixture."""
        return DenseUnit(
            in_features=10,
            out_features=10
        )

    def test_forward(self, dense_unit):
        """Confirm size is expected after forward."""
        test_input = torch.ones([1, dense_unit.in_features])
        output = dense_unit.forward(test_input)
        assert output.size() == torch.ones([1, dense_unit.out_features]).size()


class TestConvUnit:
    """To test ConvUnit layers."""

    @pytest.fixture
    def conv_unit(self):
        """Create ConvUnit fixture."""
        return ConvUnit(
            conv_dim=2,
            in_channels=10,
            out_channels=10,
            kernel_size=(5, 5)
        )

    def test_forward(self, conv_unit):
        """Confirm size is expected after forward."""
        test_input = torch.ones([1, conv_unit.in_channels, 28, 28])
        output = conv_unit.forward(test_input)
        # No padding with 2 5x5 kernels leads from 28x28 -> 24x24
        assert output.size() == torch.ones([1, conv_unit.out_channels, 24, 24]).size()


class TestSeluInit:
    """To test selu initialized layer properties."""

    @pytest.fixture
    def dense_unit(self):
        """Create a dense unit fixture."""
        return DenseUnit(
            in_features=10,
            out_features=10
        )

    @pytest.fixture
    def conv_unit(self):
        """Create a conv unit fixture."""
        return ConvUnit(
            conv_dim=2,
            in_channels=10,
            out_channels=10,
            kernel_size=(5, 5)
        )

    def test_dense_selu_weight_change(self, dense_unit):
        """Confirm SELU weight init properties hold for dense net."""
        starting_weight = copy.deepcopy(dense_unit._kernel.weight)
        fan_in = dense_unit.in_features
        std = round(math.sqrt(1. / fan_in), 1)

        dense_unit.weight_init = selu_weight_init_
        dense_unit._init_weights()
        new_weight = dense_unit._kernel.weight
        assert (torch.equal(starting_weight, new_weight) is False)
        assert pytest.approx(round(new_weight.std().item(), 1), 0.1) == std
        assert (int(new_weight.mean().item()) == 0.0)

    def test_conv_selu_weight_change(self, conv_unit):
        """Confirm SELU weight init properties hold for conv net."""
        starting_weight = copy.deepcopy(conv_unit._kernel.weight)
        fan_in = conv_unit._kernel.in_channels * \
            reduce(lambda k1, k2: k1 * k2, conv_unit._kernel.kernel_size)
        std = round(math.sqrt(1. / fan_in), 1)
        conv_unit.weight_init = selu_weight_init_
        conv_unit._init_weights()
        new_weight = conv_unit._kernel.weight
        assert (torch.equal(starting_weight, new_weight) is False)
        assert pytest.approx(round(new_weight.std().item(), 1), 0.1) == std
        assert (int(new_weight.mean().item()) == 0)

    def test_dense_selu_bias_change(self, dense_unit):
        """Confirm SELU bias init properties hold for dense net."""
        starting_bias = copy.deepcopy(dense_unit._kernel.bias)

        dense_unit.bias_init = selu_bias_init_
        dense_unit._init_bias()
        new_bias = dense_unit._kernel.bias
        assert (torch.equal(starting_bias, new_bias) is False)
        assert (round(new_bias.std().item(), 1) == 0.0)
        assert (int(new_bias.mean().item()) == 0)

    def test_conv_selu_bias_change(self, conv_unit):
        """Confirm SELU bias init properties hold for conv net."""
        starting_bias = copy.deepcopy(conv_unit._kernel.bias)

        conv_unit.bias_init = selu_bias_init_
        conv_unit._init_bias()
        new_bias = conv_unit._kernel.bias
        assert (torch.equal(starting_bias, new_bias) is False)
        assert (round(new_bias.std().item(), 1) == 0.0)
        assert (int(new_bias.mean().item()) == 0)


class TestSeluInitTrain:
    """To test selu initialization properties hold during training."""

    @pytest.fixture
    def dnn_class(self):
        """Create DenseNet with no prediction layer."""
        return DenseNet(
            name='Test_DenseNet_class',
            in_dim=(200),
            activation=torch.nn.SELU(),
            num_classes=10,
            config={
                'dense_units': [100],
                'dropout': [0.3],
            },
            optim_spec={'name': 'Adam', 'lr': 0.001}
        )

    @pytest.fixture
    def cnn_class(self):
        """Create ConvNet with prediction layer."""
        return ConvNet(
            name='Test_ConvNet_class',
            in_dim=(1, 28, 28),
            activation=torch.nn.SELU(),
            config={
                'conv_units': [
                    {
                        "in_channels": 1,
                        "out_channels": 16,
                        "kernel_size": (5, 5),
                        "stride": 2
                    },
                    {
                        "in_channels": 16,
                        "out_channels": 1,
                        "kernel_size": (5, 5),
                        "stride": 1,
                        "padding": 2
                    }]
            },
            num_classes=10
        )

    def test_selu_trained_dense(self, dnn_class):
        """Confirm SELU weight and bias properties hold for a dense net."""
        fan_in = dnn_class.in_dim[0]
        std = round(math.sqrt(1. / fan_in), 1)
        test_input = torch.ones([10, *dnn_class.in_dim]).float()
        test_target = torch.LongTensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        test_dataloader = DataLoader(TensorDataset(test_input, test_target))
        dnn_class.fit(test_dataloader, test_dataloader, 5)
        trained = dnn_class.network.dense_0._kernel
        assert (round(trained.weight.std().item(), 1) == std)
        assert (int(trained.weight.mean().item()) == 0.0)
        assert (round(trained.bias.std().item(), 1) == 0.0)
        assert (int(trained.bias.mean().item()) == 0.0)

    def test_selu_trained_conv(self, cnn_class):
        """Confirm SELU weight and bias properties hold for a conv net."""
        fan_in = cnn_class.network[0].in_channels * \
            reduce(lambda k1, k2: k1 * k2, cnn_class.network[0].kernel_size)
        std = round(math.sqrt(1. / fan_in), 1)
        test_input = torch.ones([10, *cnn_class.in_dim]).float()
        test_target = torch.LongTensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        test_dataloader = DataLoader(TensorDataset(test_input, test_target))
        cnn_class.fit(test_dataloader, test_dataloader, 5)
        trained = cnn_class.network.conv_0._kernel
        assert (round(trained.weight.std().item(), 1) == std)
        assert (int(trained.weight.mean().item()) == 0.0)
        assert (round(trained.bias.std().item(), 1) == 0.0)
        assert (int(trained.bias.mean().item()) == 0.0)
