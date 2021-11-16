"""
Sampling masked passwords (templates)
"""
import argparse
import json
import os.path
import pickle
import random
from typing import Tuple, Dict, Set, List


def read_mask(folder: str) -> Tuple[Dict[str, Set[Tuple[str, ...]]], Dict[Tuple[str, ...], Set[Tuple[str, ...]]]]:
    masked_pickle = os.path.join(folder, 'masked.pickle')
    with open(masked_pickle, 'rb') as f_masked_pickle:
        templates_dict, pwd_mask_dict = pickle.load(f_masked_pickle)
        return templates_dict, pwd_mask_dict


def sampling(templates: Set[Tuple[str, ...]], n: int, m: int):
    want = m * n
    templates = list(templates)
    while want > len(templates):
        templates.extend(templates)
        pass
    random.shuffle(templates)
    start = 0
    all_sampled = []
    for i in range(m):
        sampled = templates[start:start + n]
        start += n
        all_sampled.append(sampled)
    return all_sampled


def wrapper():
    cli = argparse.ArgumentParser('Mask sampling')
    cli.add_argument("-i", '--input-folder', dest='folder', required=True, type=str,
                     help='The folder saving the masked passwords (templates)')
    cli.add_argument('-n', '--num-samples', dest='n_samples', required=False, type=int,
                     default=30, help='the number of samples to obtain in the templates')
    cli.add_argument('-m', '--m-rounds', dest='m_rounds', required=False, type=int,
                     default=3, help='each round we obtain n samples')
    args = cli.parse_args()
    folder, n_samples, m_rounds = args.folder, args.n_samples, args.m_rounds
    templates_dict, pwd_mask_dict = read_mask(folder=folder)
    sampled_templates_dict_list: List[Dict[str, Dict[Tuple[str, ...], Set[Tuple[str, ...]]]]] = [{}] * m_rounds
    for cls_name, templates in templates_dict.items():
        all_sampled = sampling(templates=templates, n=n_samples, m=m_rounds)
        for i in range(m_rounds):
            sampled_pwd_mask_dict = {}
            samples = all_sampled[i]
            for sample in samples:
                sampled_pwd_mask_dict[sample] = pwd_mask_dict[sample]
            sampled_templates_dict_list[i][cls_name] = sampled_pwd_mask_dict
    for i in range(m_rounds):
        save_i_pickle = os.path.join(folder, f"sampled-{i}.pickle")
        with open(save_i_pickle, 'wb') as f_save_i:
            pickle.dump(sampled_templates_dict_list[i], file=f_save_i)
        save_i_json = os.path.join(folder, f"sampled-{i}.json")
        with open(save_i_json, 'w') as f_save_i_json:
            printable = {
                cls_name: {
                    " ".join(template): [" ".join(pwd) for pwd in passwords]
                    for template, passwords in template2passwords.items()
                }
                for cls_name, template2passwords in sampled_templates_dict_list[i].items()
            }
            json.dump(printable, fp=f_save_i_json, indent=2)
            pass
    pass


if __name__ == '__main__':
    wrapper()
