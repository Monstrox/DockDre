#!/usr/bin/env python

import os
import optparse
import re
import subprocess
from subprocess import *
import numpy as np
from operator import *
from scipy.misc import logsumexp


parser=optparse.OptionParser()
parser.add_option('--pdb', dest = 'pdb_file',
    default = '',    
    help = 'Protein comple in PDB format' )
    
parser.add_option('--seq', dest = 'seq_file',
    default = '',    
    help = 'Sequences file' )

parser.add_option('--nb', dest = 'nb',
    default = 5,    
    help = 'Number of docked pose taken as instance in Z computation' )

parser.add_option('--temp', dest = 'temp',
                     default = 25,
                     help = 'Temperature' )

(options,args) = parser.parse_args()

pdb_file=options.pdb_file
seq_file = options.seq_file
nb_instance=int(options.nb)
temp=options.temp
sequences=[]
sequences.append(pdb_file.split('.pdb')[0])

## parse the flexible file to get the flexibles residues
flexibles_rec=open("flexibles.receptor",'r')
flexibles_rec=flexibles_rec.readlines()[0]
flexibles_rec=[int(i) for i in flexibles_rec.split()]

flexibles_lig=open("flexibles.ligand",'r')
flexibles_lig=flexibles_lig.readlines()[0]
flexibles_lig=[int(i) for i in flexibles_lig.split()]

flexibles=sorted(flexibles_rec+flexibles_lig)

if os.path.exists( os.getcwd() + '/' + seq_file ) and seq_file:
    seqfile=open(seq_file,'r')
    for seq in seqfile.readlines():
        sequences.append(seq[:-1])
        seqfile.close()
        for mut in sequences:
            scorefile=open(os.getcwd()+'/'+mut+'/score.sc','r')
            scores=[]
            for s in scorefile.readlines():
                scores.append([int(s.split()[0]),float(s.split()[1])])
            scores.sort(key=itemgetter(1))
            scorefile.close()
            scorefile=open(os.getcwd()+'/'+mut+'/score.sc','w')
            for s in scores:
              scorefile.write(str(s[0])+' '+str(s[1])+'\n')
            scorefile.close()

if os.path.exists( os.getcwd() + '/' + seq_file ) and seq_file:
  seqfile=open(seq_file,'r')
  for seq in seqfile.readlines():
    sequences.append(seq[:-1])
  seqfile.close()
  if os.path.exists('command.txt'):
      os.remove('command.txt')
  out=open('command.txt','ab')
  for mut in sequences:
    print mut
    if os.path.exists( os.getcwd() + '/' + mut ):
      if not os.path.exists( os.getcwd() + '/' + mut+'/Z' ):
        os.mkdir(os.getcwd() + '/' + mut+'/Z')
      scorefile=open(os.getcwd()+'/'+mut+'/score.sc','r')
      score_file=scorefile.readlines()
      instances=os.listdir(os.getcwd()+'/'+mut+'/SOL')
      for instance_file in instances:
        for counter in range(0,nb_instance):
          if (instance_file!="receptor.sol") and (instance_file!="ligand.sol") and (str(int(score_file[counter].split()[0])+1) == instance_file.split('_')[1].split('.sol')[0]) and (instance_file.split('_')[1]!="min.sol"):
            instance=instance_file.split('.sol')[0]
            print "Pose:", instance_file
            f=open(os.getcwd()+'/'+mut+"/SOL/"+instance_file,'r')
            sol=[int(i) for i in f.readlines()[0].split()]
            f.close()
            opt=""
            for i in range(0,len(sol)):
              if not i+1 in flexibles:
                opt+=","+str(i)+"="+str(sol[i])
            command="toulbar2 "+os.getcwd()+"/"+mut+"/LG/"+instance+".LG " + "-logz " + "-ztmp="+temp+" -x="+opt+" > "+ os.getcwd()+"/"+mut+"/Z/"+instance+".Zlog\n"
            out.write(command)
        
        if instance_file!="receptor.sol" and instance_file!="ligand.sol" and instance_file.split('_')[1]=="min.sol":
          instance=instance_file.split('.sol')[0]
          print "Pose:", instance_file
          f=open(os.getcwd()+'/'+mut+"/SOL/"+instance_file,'r')
          sol=[int(i) for i in f.readlines()[0].split()]
          f.close()
          opt=""
          for i in range(0,len(sol)):
            if not i+1 in flexibles:
              opt+=","+str(i)+"="+str(sol[i])
          command="toulbar2 "+os.getcwd()+'/'+mut+"/LG/"+instance+".LG " + "-logz " + "-ztmp="+temp+" -x="+opt+" > "+ os.getcwd()+'/'+mut+'/Z/'+instance+'.Zlog\n'
          out.write(command)
      
      print "Receptor"
      f=open(os.getcwd()+'/'+mut+"/SOL/receptor.sol",'r')
      sol_rec=[int(i) for i in f.readlines()[0].split()]
      f.close()
      opt=""
      for i in range(0,len(sol_rec)):
        if not i+1 in flexibles_rec:
          opt+=","+str(i)+"="+str(sol_rec[i])
      command="toulbar2 "+os.getcwd()+'/'+mut+"/LG/receptor.LG "+"-logz "+" -ztmp="+temp+" -x="+opt+" > "+ os.getcwd()+'/'+mut+'/Z/'+"receptor.Zlog\n"
      out.write(command)
      
      print "Ligand"
      flexibles_lig_renum=[i-int(len(sol_rec)) for i in flexibles_lig]
      f=open(os.getcwd()+'/'+mut+"/SOL/ligand.sol",'r')
      sol_lig=[int(i) for i in f.readlines()[0].split()]
      f.close()
      opt=""
      for i in range(0,len(sol_lig)):
        if not i+1 in flexibles_lig_renum:
          opt+=","+str(i)+"="+str(sol_lig[i])
      command="toulbar2 "+os.getcwd()+'/'+mut+"/LG/ligand.LG "+"-logz "+"-ztmp="+temp+" -x="+opt+" > "+ os.getcwd()+'/'+mut+'/Z/'+"ligand.Zlog\n"
      out.write(command)
out.close()

    
