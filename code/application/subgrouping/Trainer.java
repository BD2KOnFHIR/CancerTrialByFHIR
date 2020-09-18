package main;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.CmdLineParser;

import eval.ClusteringEval;
import models.GibbsSamplingDMM;
import models.GibbsSamplingDMM_Inf;
import models.GibbsSamplingLDA;
import models.GibbsSamplingLDA_Inf;
import utility.CmdArgs;
import utility.MTRandom;

public class Trainer {
	
	
	public static ArrayList<Boolean> readLabel(String file) throws IOException{
		
		ArrayList<Boolean> list=new ArrayList<>();
		BufferedReader br=new BufferedReader(new FileReader(new File(file)));
		String line=null;
		while((line=br.readLine())!=null){
			if(line.contains("q12:_assigned_treatment_(medication)")){
				list.add(true);
			}else{
				list.add(false);
			}
		}
		return list;
	}
	
	public static void train(){
		CmdArgs cmdArgs = new CmdArgs();
		
		String model="DMM"; //DMM,LDAinf,DMMinf,Eval
		String file="/infodev1/home/m205410/data/cancer_trail/CRF_LDA_trainning_realPatient.tsv";
//		String file="/infodev1/home/m205410/data/cancer_trail/CRF_LDA_trainning.tsv";
		MTRandom.setSeed(1024);
		cmdArgs.model=model;
		cmdArgs.corpus=file;
		cmdArgs.ntopics=4;
		cmdArgs.niters=10000;
		cmdArgs.expModelName=model+"_"+cmdArgs.ntopics;
		cmdArgs.twords=10;
		cmdArgs.twords_ratio=0.01;
		try {

			if (cmdArgs.model.equals("LDA")) {
				GibbsSamplingLDA lda = new GibbsSamplingLDA(cmdArgs.corpus,
					cmdArgs.ntopics, cmdArgs.alpha, cmdArgs.beta,
					cmdArgs.niters, cmdArgs.twords, cmdArgs.expModelName,
					cmdArgs.initTopicAssgns, cmdArgs.savestep);
				lda.inference();
			}
			else if (cmdArgs.model.equals("DMM")) {
				GibbsSamplingDMM dmm = new GibbsSamplingDMM(cmdArgs.corpus,
					cmdArgs.ntopics, cmdArgs.alpha, cmdArgs.beta,
					cmdArgs.niters, cmdArgs.twords, cmdArgs.expModelName,
					cmdArgs.initTopicAssgns, cmdArgs.savestep,cmdArgs.twords_ratio);
				dmm.inference();
			}
			else if (cmdArgs.model.equals("LDAinf")) {
				GibbsSamplingLDA_Inf lda = new GibbsSamplingLDA_Inf(
					cmdArgs.paras, cmdArgs.corpus, cmdArgs.niters,
					cmdArgs.twords, cmdArgs.expModelName, cmdArgs.savestep);
				lda.inference();
			}
			else if (cmdArgs.model.equals("DMMinf")) {
				GibbsSamplingDMM_Inf dmm = new GibbsSamplingDMM_Inf(
					cmdArgs.paras, cmdArgs.corpus, cmdArgs.niters,
					cmdArgs.twords, cmdArgs.expModelName, cmdArgs.savestep);
				dmm.inference();
			}
			else if (cmdArgs.model.equals("Eval")) {
				ClusteringEval.evaluate(cmdArgs.labelFile, cmdArgs.dir,
					cmdArgs.prob);
			}
			else {
				System.out
					.println("Error: Option \"-model\" must get \"LDA\" or \"DMM\" or \"LDAinf\" or \"DMMinf\" or \"Eval\"");
				System.out
					.println("\tLDA: Specify the Latent Dirichlet Allocation topic model");
				System.out
					.println("\tDMM: Specify the one-topic-per-document Dirichlet Multinomial Mixture model");
				System.out
					.println("\tLDAinf: Infer topics for unseen corpus using a pre-trained LDA model");
				System.out
					.println("\tDMMinf: Infer topics for unseen corpus using a pre-trained DMM model");
				System.out
					.println("\tEval: Specify the document clustering evaluation");
				return;
			}
		}
		catch (CmdLineException cle) {
			System.out.println("Error: " + cle.getMessage());
			return;
		}
		catch (Exception e) {
			System.out.println("Error: " + e.getMessage());
			e.printStackTrace();
			return;
		}
		
	}
	
	
	
	public static void test(){
		CmdArgs cmdArgs = new CmdArgs();
		
		String model="Eval"; //DMM,LDAinf,DMMinf,Eval
		MTRandom.setSeed(1024);
		cmdArgs.model=model;
		cmdArgs.labelFile="/infodev1/home/m205410/workspace/java/jLDADMM-master/jLDADMM-master/test/corpus.LABEL";
		cmdArgs.dir="/infodev1/home/m205410/workspace/java/jLDADMM-master/jLDADMM-master/test";
		cmdArgs.prob="DMM.theta";
		
		System.out.println(cmdArgs.model);
		System.out.println(cmdArgs.labelFile);
		System.out.println(cmdArgs.dir);
		System.out.println(cmdArgs.prob);
		try {

			if (cmdArgs.model.equals("LDA")) {
				GibbsSamplingLDA lda = new GibbsSamplingLDA(cmdArgs.corpus,
					cmdArgs.ntopics, cmdArgs.alpha, cmdArgs.beta,
					cmdArgs.niters, cmdArgs.twords, cmdArgs.expModelName,
					cmdArgs.initTopicAssgns, cmdArgs.savestep);
				lda.inference();
			}
			else if (cmdArgs.model.equals("DMM")) {
				GibbsSamplingDMM dmm = new GibbsSamplingDMM(cmdArgs.corpus,
					cmdArgs.ntopics, cmdArgs.alpha, cmdArgs.beta,
					cmdArgs.niters, cmdArgs.twords, cmdArgs.expModelName,
					cmdArgs.initTopicAssgns, cmdArgs.savestep);
				dmm.inference();
			}
			else if (cmdArgs.model.equals("LDAinf")) {
				GibbsSamplingLDA_Inf lda = new GibbsSamplingLDA_Inf(
					cmdArgs.paras, cmdArgs.corpus, cmdArgs.niters,
					cmdArgs.twords, cmdArgs.expModelName, cmdArgs.savestep);
				lda.inference();
			}
			else if (cmdArgs.model.equals("DMMinf")) {
				GibbsSamplingDMM_Inf dmm = new GibbsSamplingDMM_Inf(
					cmdArgs.paras, cmdArgs.corpus, cmdArgs.niters,
					cmdArgs.twords, cmdArgs.expModelName, cmdArgs.savestep);
				dmm.inference();
			}
			else if (cmdArgs.model.equals("Eval")) {
				ClusteringEval.evaluate(cmdArgs.labelFile, cmdArgs.dir,
					cmdArgs.prob);
			}
			else {
				System.out
					.println("Error: Option \"-model\" must get \"LDA\" or \"DMM\" or \"LDAinf\" or \"DMMinf\" or \"Eval\"");
				System.out
					.println("\tLDA: Specify the Latent Dirichlet Allocation topic model");
				System.out
					.println("\tDMM: Specify the one-topic-per-document Dirichlet Multinomial Mixture model");
				System.out
					.println("\tLDAinf: Infer topics for unseen corpus using a pre-trained LDA model");
				System.out
					.println("\tDMMinf: Infer topics for unseen corpus using a pre-trained DMM model");
				System.out
					.println("\tEval: Specify the document clustering evaluation");
				return;
			}
		}
		catch (CmdLineException cle) {
			System.out.println("Error: " + cle.getMessage());
			return;
		}
		catch (Exception e) {
			System.out.println("Error: " + e.getMessage());
			e.printStackTrace();
			return;
		}
		
	}
	
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		train();
//		test();
		
		
	}

}
