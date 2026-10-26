"""Reproduce the official NPI RNN demo for one simulation seed.

This script intentionally calls the original NPI.py implementation without
changing its training or perturbation logic.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch
from scipy.stats import pearsonr

import NPI


def off_diagonal(matrix):
    mask = ~np.eye(matrix.shape[0], dtype=bool)
    return matrix[mask]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--output", default="reproduction_results")
    args = parser.parse_args()

    # Make the reproduction repeatable. The upstream notebook does not set
    # these seeds, so its metrics can vary slightly between runs.
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    root = Path("RNN_simulation_data/sim_data")
    tag = f"{args.seed:02d}"
    signals = np.loadtxt(root / f"dynamics_020nodes_8000steps_{tag}seed.txt")
    structural_connectivity = np.loadtxt(root / f"SC_020nodes_8000steps_{tag}seed.txt")
    real_ec = np.loadtxt(root / f"real_EC_020nodes_8000steps_{tag}seed.txt")

    roi_num = signals.shape[1]
    steps = 3
    inputs, targets = NPI.multi2one(signals, steps=steps)
    model = NPI.ANN_MLP(
        input_dim=steps * roi_num,
        hidden_dim=2 * roi_num,
        latent_dim=int(0.8 * roi_num),
        output_dim=roi_num,
    )
    model, train_loss, test_loss = NPI.train_NN(
        model,
        inputs,
        targets,
        batch_size=50,
        train_set_proportion=0.8,
        num_epochs=args.epochs,
        lr=2e-4,
        l2=5e-5,
    )

    empirical_fc = NPI.corrcoef(signals)
    model_fc = NPI.model_FC(model, node_num=roi_num, steps=steps)
    npi_ec = NPI.model_EC(model, inputs, targets, pert_strength=1.0)

    metrics = {
        "seed": args.seed,
        "epochs": args.epochs,
        "signals_shape": list(signals.shape),
        "input_shape": list(inputs.shape),
        "final_train_mse": float(train_loss[-1]),
        "final_test_mse": float(test_loss[-1]),
        "model_fc_vs_empirical_fc_r": float(
            pearsonr(off_diagonal(model_fc), off_diagonal(empirical_fc))[0]
        ),
        "npi_ec_vs_real_ec_r": float(
            pearsonr(off_diagonal(npi_ec), off_diagonal(real_ec))[0]
        ),
        "npi_ec_vs_sc_r": float(
            pearsonr(off_diagonal(npi_ec), off_diagonal(structural_connectivity))[0]
        ),
    }

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / f"rnn_seed{tag}_metrics.json").write_text(json.dumps(metrics, indent=2))
    np.save(output / f"rnn_seed{tag}_model_fc.npy", model_fc)
    np.save(output / f"rnn_seed{tag}_npi_ec.npy", npi_ec)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
