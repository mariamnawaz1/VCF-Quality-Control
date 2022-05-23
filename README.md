# VCF-Quality-Control
Script to perform quality control on Genomics files (VCF files)

## usage: 
#1. If using --indep utility
#  ./QC_script.py -i <input_vcf_name.vcf> [-m] [-maf] [-g] [-hw] [-f] [-s] [-ldp] [-indep_w] [-indep_s] [-indep_v]

#2 If using --indep-pairwise utility
# ./QC_script.py -i <input_vcf_name.vcf> [-m] [-maf] [-g] [-hw] [-f] [-s] [-ldp] [-indep_w] [-indep_s] [-indep_t] 


# Example1: ./QC_script.py -i GC123.vcf -m 0.05 -maf 0.05 -g 0.1 -hw 0.00000001 -f 0.05 -s 0.1 -ldp i -indep_w 50 -indep_s 5 -indep_v 2
# Example2: ./QC_script.py -i GC123.vcf -m 0.05 -maf 0.05 -g 0.1 -hw 0.00000001 -f 0.05 -s 0.1 -ldp ip -indep_w 50 -indep_s 5 -indep_t 0.5

