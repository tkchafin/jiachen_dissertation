import pysam
import os
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.model_selection import KFold
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, silhouette_score, fowlkes_mallows_score, completeness_score
from unlda import *
from unrtlda import *
from unrtlda_a import *
from untrlda import *
from untrlda_a import *
from swulda import *
from unrtcdlda import *
from untrcdlda import *
from unkfdapc import *
from grid_search import *

def main():

    # Paths to the example files
    vcf_path = "terrapene.filtered.vcf.gz"
    popmap_path = "terrapene_popmap.csv"

    # Extract genotype matrix and population labels
    genotype_matrix, pop_labels = vcf_to_matrix(vcf_path, popmap_path)

    label_encoder = LabelEncoder()
    pop_labels = label_encoder.fit_transform(pop_labels)

    # Print the shape of the matrix and some labels as a sanity check
    print("Genotype Matrix Shape:", genotype_matrix.shape)
    print("Genotype Matrix:\n", genotype_matrix)
    print("Population Labels:", pop_labels[:10])

    max_iter = 500
    k_range = range(8, 1,-1)
    Npc_range = range(300, 49, -50)

    grid_search_clustering(genotype_matrix, pop_labels, k_range, Npc_range, max_iter, datatype='terrapene_5', method='un_rtlda')
    #grid_search_clustering(genotype_matrix, pop_labels, k_range, Npc_range, max_iter, datatype='terrapene_5', method='un_trlda')
    #grid_search_clustering(genotype_matrix, pop_labels, k_range, Npc_range, max_iter, datatype='terrapene_5', method='un_lda')

    grid_search_clustering(genotype_matrix, pop_labels, k_range, Npc_range, max_iter, datatype='terrapene_5', method='un_rtalda')
    #grid_search_clustering(genotype_matrix, pop_labels, k_range, Npc_range, max_iter, datatype='terrapene_5', method='un_tralda')
    #grid_search_clustering(genotype_matrix, pop_labels, k_range, Npc_range, max_iter, datatype='terrapene_5', method='swulda')

    grid_search_clustering(genotype_matrix, pop_labels, k_range, Npc_range, max_iter, datatype='terrapene_5', method='un_rtcdlda')
    #grid_search_clustering(genotype_matrix, pop_labels, k_range, Npc_range, max_iter, datatype='terrapene_5', method='un_trcdlda')
    #grid_search_clustering(genotype_matrix, pop_labels, k_range, Npc_range, max_iter, datatype='terrapene_5', method='un_kfdapc')
def vcf_to_matrix(vcf_path, popmap_path):
    # Create an index with tabix if it doesn't exist
    if not (os.path.exists(vcf_path + '.tbi') or os.path.exists(vcf_path + '.csi')):
        pysam.tabix_index(vcf_path, preset='vcf')

    # Read popmap to create a dictionary for individual labels
    popmap = pd.read_csv(popmap_path, header=None, names=["ind", "pop"])
    popmap_dict = pd.Series(popmap["pop"].values, index=popmap["ind"]).to_dict()

    # Open VCF file using pysam
    vcf = pysam.VariantFile(vcf_path)
    samples = list(vcf.header.samples)
    num_individuals = len(samples)
    num_variants = sum(1 for _ in vcf.fetch())

    # Initialize matrix and labels list
    genotype_matrix = np.zeros((num_individuals, num_variants), dtype=int)
    pop_labels = [popmap_dict.get(sample, 'Unknown') for sample in samples]

    # Re-open VCF to iterate over it again
    vcf = pysam.VariantFile(vcf_path)
    variant_idx = 0
    for record in vcf.fetch():
        for ind_idx, ind in enumerate(samples):
            sample = record.samples[ind]
            gt = sample['GT']
            if gt == (0, 0):
                genotype_matrix[ind_idx, variant_idx] = 0  # Homozygous reference
            elif gt == (0, 1) or gt == (1, 0):
                genotype_matrix[ind_idx, variant_idx] = 1  # Heterozygous
            elif gt == (1, 1):
                genotype_matrix[ind_idx, variant_idx] = 2  # Homozygous alternate
        variant_idx += 1

    return genotype_matrix, pop_labels



if __name__ == "__main__":
    main()