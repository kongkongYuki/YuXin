import argparse
from OpenHINE.src.config import Config
from OpenHINE.src.utils.data_process import *
from OpenHINE.src.model.Metapath2vec import *

import warnings
import os

from OpenHINE.src.utils.hete_random_walk import random_walk_based_mp, MetaGraphGenerator

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
warnings.filterwarnings('ignore')

seed = 0


def model_main():
    args = init_para()

    config_file = ["/Users/xinyu/Documents/Dissertation/LegalWeb/OpenHINE/src/config.ini"]
    config = Config(config_file, args)


    g_hin = HIN(config.input_fold, config.data_type, config.relation_list) #

    if args.model == "Metapath2vec":
        config.temp_file += args.dataset + '_' + config.metapath + '.txt'
        config.out_emd_file += args.dataset + '_' + config.metapath + '.txt'

        random_walk_based_mp(g_hin, config.metapath, config.num_walks, config.walk_length, config.temp_file)
        m2v = Metapath2VecTrainer(config, g_hin)
        m2v.train()

    elif args.model == "MetaGraph2vec":
        config.temp_file += 'graph_rw.txt'
        config.out_emd_file += args.dataset + '_node.txt'
        mgg = MetaGraphGenerator()
        if args.dataset == "acm":
            mgg.generate_random_three(config.temp_file, config.num_walks, config.walk_length, g_hin.node,
                                      g_hin.relation_dict)
        elif args.dataset == "test":
            mgg.generate_random_four(config.temp_file, config.num_walks, config.walk_length, g_hin.node,
                                     g_hin.relation_dict)
        elif args.dataset == "dblp":
            mgg.generate_random_four(config.temp_file, config.num_walks, config.walk_length, g_hin.node,
                                     g_hin.relation_dict)
        model = Metapath2VecTrainer(config, g_hin)
        print("Training")
        model.train()


def init_para():
    parser = argparse.ArgumentParser(description="OPEN-HINE")
    parser.add_argument('-d', '--dataset', default='test', type=str, help="Dataset")
    parser.add_argument('-m', '--model', default='MetaGraph2vec', type=str, help='Train model')

    args = parser.parse_args()
    return args

# if __name__ == "__main__":
#     main()
