import argparse
import json
import os.path
import random
from typing import List, Dict, Set, Tuple

import pickle


def read_template_dicts(folder: str) -> Tuple[List[Dict[str, Set[str]]], List[str]]:
    file_list_pickle = os.path.join(folder, 'file_list.pickle')
    with open(file_list_pickle, 'rb') as f_file_list_pickle:
        pwd_mask_file_list, template_file_list = pickle.load(f_file_list_pickle)
        template_dicts = []
        for template_file in template_file_list:
            with open(os.path.join(folder, template_file), 'rb') as f_template:
                template_dict = pickle.load(f_template)
                template_dicts.append(template_dict)
            pass
    return template_dicts, pwd_mask_file_list


def sampling(template_dicts: List[Dict[str, Set[str]]], n_samples: int):
    universe = {}
    for template_dict in template_dicts:
        for cls_name, templates in template_dict.items():
            if cls_name not in universe:
                universe[cls_name] = set()
            universe[cls_name] = universe[cls_name].union(templates)

        pass
    final_samples, template2passwords = {}, {}
    for cls_name, templates in universe.items():
        total = len(templates)
        if total < n_samples:
            selections = [True] * total
        else:
            selections = [True] * n_samples + [False] * (total - n_samples)
            random.shuffle(selections)
        samples = []
        for selection, template in zip(selections, templates):
            if selection:
                samples.append(template)
                template2passwords[template] = set()

        final_samples[cls_name] = samples
        pass
    return final_samples, template2passwords


def wrapper():
    cli = argparse.ArgumentParser('Mask sampling')
    cli.add_argument("-i", '--input-folder', dest='input', required=True, type=str,
                     help='the pickle file saving the file lists')
    cli.add_argument("-n", '--n-samples', dest='n_samples', required=False, type=int, default=30,
                     help='n samples for each class of templates')
    cli.add_argument("--dup", dest='dup_factor', required=False, type=int, default=1,
                     help='set the times of sampling')
    args = cli.parse_args()
    folder, n_samples, dup_factor = args.input, args.n_samples, args.dup_factor
    template_dicts, pwd_mask_file_list = read_template_dicts(folder)
    for i in range(dup_factor):
        samples, template2passwords = sampling(template_dicts=template_dicts, n_samples=n_samples)
        for pwd_mask_file in pwd_mask_file_list:
            with open(os.path.join(folder, pwd_mask_file), 'rb') as f_pwd_mask:
                pwd_mask_dict: Dict[Tuple, Tuple] = pickle.load(f_pwd_mask)
                for masked, passwords in pwd_mask_dict.items():
                    if masked in template2passwords:
                        template2passwords[masked] = template2passwords[masked].union(passwords)
                del pwd_mask_dict
        tag_i = f"sampled-{i}"
        saved_filename = os.path.join(folder, f'{tag_i}.pickle')
        saved_json = os.path.join(folder, f'{tag_i}.json')
        with open(saved_filename, 'wb') as f_save:
            print(f"pickle file is saved here: {saved_filename}")
            pickle.dump((samples, template2passwords), file=f_save)
        with open(saved_json, 'w') as f_save:
            print(f"json file is saved here: {saved_json}")
            samples_printable = {cls_name: [" ".join(i) for i in v] for cls_name, v in samples.items()}
            template2passwords_printable = {" ".join(k): [" ".join(i) for i in v] for k, v in
                                            template2passwords.items()}
            json.dump((samples_printable, template2passwords_printable), fp=f_save, indent=2)
        del samples, samples_printable, template2passwords_printable, template2passwords
        pass


if __name__ == '__main__':
    wrapper()
