import pytest

import torch
from torch.utils.data import TensorDataset

from vulcanai2.datasets import MultiDataset
from vulcanai2.models import ConvNet, DenseNet

@pytest.fixture(scope="module")
def conv1D_net():
    """conv1D fixture."""
    return ConvNet(
        name='conv1D_net',
        in_dim=(1, 28),
        config={
            'conv_units': [
                dict(
                    in_channels=1,
                    out_channels=24,
                    kernel_size=(5),
                    stride=2,
                    pool_size=2,
                    dropout=0.1
                ),
                dict(
                    in_channels=24,
                    out_channels=64,
                    kernel_size=(5),
                    pool_size=2,
                    dropout=0.1
                )
            ],
        },
        device='cpu'
    )

@pytest.fixture(scope="module")
def conv2D_net():
    """conv2D fixture."""
    return ConvNet(
        name='conv2D_net',
        in_dim=(1, 28, 28),
        config={
            'conv_units': [
                dict(
                    in_channels=1,
                    out_channels=24,
                    kernel_size=(5, 5),
                    stride=2,
                    pool_size=2,
                    dropout=0.1
                ),
                dict(
                    in_channels=24,
                    out_channels=64,
                    kernel_size=(5, 5),
                    pool_size=2,
                    dropout=0.1
                )
            ],
        },
        device='cpu'
    )

@pytest.fixture(scope="module")
def conv3D_net():
    """conv3D fixture."""
    return ConvNet(
        name='conv3D_net',
        in_dim=(1, 28, 28, 28),
        config={
            'conv_units': [
                dict(
                    in_channels=1,
                    out_channels=16,
                    kernel_size=(5, 5, 5),
                    stride=2,
                    dropout=0.1
                ),
                dict(
                    in_channels=16,
                    out_channels=64,
                    kernel_size=(5, 5, 5),
                    dropout=0.1
                )
            ],
        },
        device='cpu'
    )

@pytest.fixture(scope="module")
def conv3D_net_class():
    """conv3D fixture."""
    return ConvNet(
        name='conv3D_net',
        in_dim=(1, 28, 28, 28),
        num_classes=10,
        config={
            'conv_units': [
                dict(
                    in_channels=1,
                    out_channels=16,
                    kernel_size=(5, 5, 5),
                    stride=2,
                    dropout=0.1
                ),
                dict(
                    in_channels=16,
                    out_channels=64,
                    kernel_size=(5, 5, 5),
                    dropout=0.1
                )
            ],
        },
        device='cpu'
    )

@pytest.fixture(scope="module")
def multi_input_dnn(conv1D_net, conv2D_net):
    """Dense network fixture with two inputs."""
    return DenseNet(
        name='multi_input_dnn',
        input_networks=[conv1D_net, conv2D_net],
        config={
            'dense_units': [100, 50],
            'initializer': None,
            'bias_init': None,
            'norm': None,
            'dropout': 0.5,  # Single value or List
        },
        device='cpu'
    )

@pytest.fixture(scope="module")
def multi_input_cnn(conv2D_net, conv3D_net, multi_input_dnn):
    """Bottom multi-input network fixture."""
    return ConvNet(
        name='multi_input_cnn',
        input_networks=[conv2D_net, conv3D_net, multi_input_dnn],
        num_classes=10,
        config={
            'conv_units': [
                dict(
                    in_channels=1,
                    out_channels=16,
                    kernel_size=(3, 3, 3),
                    stride=2,
                    dropout=0.1
                ),
            ],
        },
        device='cpu'
    )
@pytest.fixture(scope="module")
def multi_input_dnn_data(conv1D_net, conv2D_net,
                         multi_input_dnn):
    return MultiDataset([
        (
            TensorDataset(
                torch.ones([10, *conv1D_net.in_dim]),
                torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]).long()),
            True, True),
        (
            TensorDataset(torch.ones(
                [10, *multi_input_dnn.input_networks['conv2D_net'].in_dim])),
            True, False)
    ])

@pytest.fixture(scope="module")
def multi_input_cnn_data(conv2D_net, conv3D_net, multi_input_dnn_data):
    return MultiDataset([
        (TensorDataset(torch.ones([10, *conv2D_net.in_dim])), True, False),
        (TensorDataset(torch.ones([10, *conv3D_net.in_dim])), True, False),
        multi_input_dnn_data
    ])

@pytest.fixture(scope="module")
def multi_input_cnn_add_input_network(conv1D_net, conv2D_net,
                                      conv3D_net):
    """Create ConvNet with input_network added via
    add_input_network and has a prediction layer."""
    net = ConvNet(
        name='multi_input_cnn_add_input_network',
        num_classes=10,
        in_dim=conv3D_net.out_dim,
        config={
            'conv_units': [
                dict(
                    in_channels=conv3D_net.out_dim[0],
                    out_channels=16,
                    kernel_size=(3, 3, 3),
                    stride=2,
                    dropout=0.1
                ),
            ],
        },
        device='cpu'
    )
    net.add_input_network(conv3D_net)
    return net