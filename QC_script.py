#!/usr/bin/env python3

## written by Mariam Nawaz
## script to perform quality control on vcf files
## usage: 
#1. If using --indep utility
#  ./QC_script.py -i <input_vcf_name.vcf> [-m] [-maf] [-g] [-hw] [-f] [-s] [-ldp] [-indep_w] [-indep_s] [-indep_v]

#2 If using --indep-pairwise utility
# ./QC_script.py -i <input_vcf_name.vcf> [-m] [-maf] [-g] [-hw] [-f] [-s] [-ldp] [-indep_w] [-indep_s] [-indep_t] 


# Example1: ./QC_script.py -i GC123.vcf -m 0.05 -maf 0.05 -g 0.1 -hw 0.00000001 -f 0.05 -s 0.1 -ldp i -indep_w 50 -indep_s 5 -indep_v 2
# Example2: ./QC_script.py -i GC123.vcf -m 0.05 -maf 0.05 -g 0.1 -hw 0.00000001 -f 0.05 -s 0.1 -ldp ip -indep_w 50 -indep_s 5 -indep_t 0.5

import subprocess
import argparse
import os

parser = argparse.ArgumentParser(description="Quality Control of Genomics files")
parser.add_argument("-i", "--input", help="Name of the input file", required=True)
parser.add_argument("-m", "--m", help="QC: Missing rate per person") # 0.1
parser.add_argument("-maf", "--maf", help="QC: Allele frequency") # 0.05
parser.add_argument("-g", "--g", help="QC: Missing rate per SNP") # 0.1
parser.add_argument("-hw", "--hw", help="QC: Hardy-Weinberg Equilibrium") # 0.0000001
parser.add_argument("-f", "--f", help="family wise- QC: Mendel error rate") # 0.05
parser.add_argument("-s", "--s", help="SNP wise- QC: Mendel error rate") # 0.1
parser.add_argument("-ldp", "--ldprune", help="Choose between indep and indep-pairwise. Type 'i' or 'ip' respectively") # 50

parser.add_argument("-indep_w", "--indep_window", help="window size for indep/indep-pairwise") # 50
parser.add_argument("-indep_s", "--indep_snp", help="Number of SNPs to shift the window in indep/indep-pairwise") # 5
parser.add_argument("-indep_v", "--indep_vif", help="VIF threshold for indep(only use if selected indep option)") # 2
parser.add_argument("-indep_t", "--indep_threshold", help=" r^2 threshold for indep-pairwise(only use if selected indep-pairwise option)") # 0.5

args = parser.parse_args()

# 1. Converting vcf to binary plink files
def vcf_to_plink(input):
    subprocess.call(["plink", "--vcf", input, "--make-bed", "--out", input])


def quality_control(**kwargs):
    
    # 2. Basic Quality controlling
    subprocess.call(["plink", "--bfile", args.input, "--allow-no-sex", "--make-founders", "--make-bed", "--out", "basicQC"])


    # 3. QC: Missing rate per person (exclude individuals with too much missing genotype data)
    subprocess.call(["plink", "--bfile", "basicQC", "--mind", kwargs.get("m"), "--make-bed", "--out", "mindQC"])

    
    # 4.QC: Allele frequency (exclude SNPs on the basis of MAF)
    subprocess.call(["plink", "--bfile", "mindQC", "--maf", kwargs.get("maf"), "--make-bed", "--out", "mafQC"])

    
    # 5.QC: Missing rate per SNP (exclude SNPs based on missing genotype rate)
    subprocess.call(["plink", "--bfile", "mafQC", "--geno", kwargs.get("g"), "--make-bed", "--out", "genoQC"])


    # 6.QC: Hardy-Weinberg Equilibrium (exclude markers that failure the Hardy-Weinberg test at a specified significance threshold)
    subprocess.call(["plink", "--bfile", "genoQC", "--hwe", kwargs.get("hw"), "--make-bed", "--out", "hweQC"])


    # 7.QC: Mendel error rate (For family-based data only, to exclude individuals and/or markers on the basis on Mendel error rate)
    subprocess.call(["plink", "--bfile", "hweQC", "--me", kwargs.get("f"), kwargs.get("s"), "--make-bed", "--out", "mendelQC"])



# 8.LD pruning of the Quality controlled data
def LD_pruning_indep(**kwargs):
    ## --indep which prunes based on the variance inflation factor (VIF), which recursively removes SNPs within a sliding window
    subprocess.call(["plink", "--bfile", "mendelQC", "--indep", kwargs.get("indep_w"), kwargs.get("indep_snp"), kwargs.get("indep_vif")])
    with open("plink.log","r") as fp:
        for line in fp:
            if line.startswith("Warning: Skipping --indep"):
                # pruning couldn't be done; possible reasons: less than 2 founders
                return 0

    # if there is no error, that means pruning has been done
    os.system("plink --bfile mendelQC --extract plink.prune.in --make-bed --out pruned_data")
    return 1

def LD_pruning_indep_pair(**kwargs):    
    ## --indep-pairwise which is similar, except it is based only on pairwise genotypic correlation.
    subprocess.call(["plink", "--bfile", "mendelQC", "--indep-pairwise", kwargs.get("indep_w"), kwargs.get("indep_snp"), kwargs.get("indep_threshold")])
    with open("plink.log","r") as fp:
        for line in fp:
            if line.startswith("Warning: Skipping --indep-pairwise"):
                # pruning couldn't be done; possible reasons: less than 2 founders
                return 0
    
    os.system("plink --bfile mendelQC --extract plink.prune.in --make-bed --out pruned_data")
    return 1



# 9.Converting pruned file back to vcf
def plink_to_vcf(input, result):
    out_file = input.split(".")[0]+"_pruned"

    if result == 0: # ld_pruning couldn't be performed --> making final vcf from MendelQC step
        subprocess.call(["plink", "--bfile", "mendelQC", "--recode", "vcf", "--out", out_file])

    else: # making final vcf of pruned file
        subprocess.call(["plink", "--bfile", "pruned_data", "--recode", "vcf", "--out", out_file])



if __name__ == "__main__":
    vcf_to_plink(args.input)

    quality_control(m=str(args.m), maf=str(args.maf), g=str(args.g), hw=str(args.hw), f=str(args.f), s=str(args.s))

    if args.ldprune == 'i':
        result = LD_pruning_indep(indep_w=args.indep_window, indep_snp=args.indep_snp, indep_vif=args.indep_vif)

    else:
        result = LD_pruning_indep_pair(indep_w=args.indep_window, indep_snp=args.indep_snp, indep_threshold=args.indep_threshold)

    plink_to_vcf(args.input, result)

    print("Done, Exiting!!!")

