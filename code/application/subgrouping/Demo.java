package main;


import java.awt.Dimension;
import java.awt.GridLayout;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

import javax.swing.JCheckBox;
import javax.swing.JComponent;
import javax.swing.JFrame;
import javax.swing.JPanel;

import smile.data.DataFrame;
import smile.manifold.TSNE;
import smile.math.matrix.DenseMatrix;
import smile.plot.Palette;
import smile.plot.PlotCanvas;
import smile.projection.PCA;
import smile.projection.RandomProjection;
import smile.math.MathEx;

@SuppressWarnings("serial")

public class Demo extends ProjectionDemo {

    JCheckBox sparseBox;

    public Step2_PCAProjectionDemo() {
        sparseBox = new JCheckBox("Sparse Random Projection");
        optionPane.add(sparseBox);
    }

    @Override
    public JComponent learn(double[][] data, int[] labels, String[] names) {
        JPanel pane = new JPanel(new GridLayout(1, 2));

        long clock = System.currentTimeMillis();
        PCA pca = PCA.cor(data);
        System.out.format("Learn PCA from %d samples in %dms\n", data.length, System.currentTimeMillis() - clock);

        pca.setProjection(2);
        double[][] y_1 = pca.project(data);
        
        /**
         * Adds a scatter plot to this canvas.
         * @param data a n-by-2 or n-by-3 matrix that describes coordinates of points.
         * @param legend the legend used to draw points.
         * <ul>
         * <li> . : dot
         * <li> + : +
         * <li> - : -
         * <li> | : |
         * <li> * : star
         * <li> x : x
         * <li> o : circle
         * <li> O : large circle
         * <li> @ : solid circle
         * <li> # : large solid circle
         * <li> s : square
         * <li> S : large square
         * <li> q : solid square
         * <li> Q : large solid square
         * <li> others : dot
         * </ul>
         * @return the scatter plot for the given points.
         */
        String file="/infodev1/home/m205410/data/cancer_trail/CRF_LDA_trainning.tsv";
        ArrayList<Boolean> list=new ArrayList<>();
		BufferedReader br = null;
		try {
			br = new BufferedReader(new FileReader(new File(file)));
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		String line=null;
		try {
			while((line=br.readLine())!=null){
				if(line.contains("q12:_assigned_treatment_(medication)")){
					list.add(true);
				}else{
					list.add(false);
				}
			}
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
        PlotCanvas plot = new PlotCanvas(MathEx.colMin(y_1), MathEx.colMax(y_1));
        if (names != null) {
            plot.points(y_1, names);
        } else if (labels != null) {
            for (int i = 0; i < y_1.length; i++) {
            	if(list.get(i)){
            		 plot.point('#', Local_Palatte.COLORS[labels[i]], y_1[i]);	
            	}else{
            		 plot.point('O', Local_Palatte.COLORS[labels[i]], y_1[i]);
            	}
               
            }
        } else {
            plot.points(y_1, pointLegend);
        }

        plot.setTitle("PCA-2D");
        pane.add(plot);

        pca.setProjection(3);
        y_1 = pca.project(data);
        
        plot = new PlotCanvas(MathEx.colMin(y_1), MathEx.colMax(y_1));
        if (names != null) {
            plot.points(y_1, names);
        } else if (labels != null) {
            for (int i = 0; i < y_1.length; i++) {
            	if(list.get(i)){
            		  plot.point('#', Local_Palatte.COLORS[labels[i]], y_1[i]);	
            	}else{
            		  plot.point('O', Local_Palatte.COLORS[labels[i]], y_1[i]);
            	}
              
            }
        } else {
            plot.points(y_1, pointLegend);
        }

        plot.setTitle("PCA-3D");
        pane.add(plot);

//        RandomProjection rp = sparseBox.isSelected() ? RandomProjection.sparse(data[0].length, 0) : RandomProjection.of(data[0].length, 2);
//        System.out.format("%d x %d Random Projection:\n", data[0].length, 3);
//        DenseMatrix projection = rp.getProjection();
//        for (int i = 0; i < projection.nrows(); i++) {
//            for (int j = 0; j < projection.ncols(); j++) {
//                System.out.format("% .4f ", projection.get(i, j));
//            }
//            System.out.println();
//        }
//        y = rp.project(data);
        
//        TSNE tsne =new TSNE(data, 2);
//        double[][] y_2=tsne.coordinates;
//
//        
//        plot = new PlotCanvas(MathEx.colMin(y_2), MathEx.colMax(y_2));
//        if (names != null) {
//            plot.points(y_2, names);
//        } else if (labels != null) {
//            for (int i = 0; i < y_2.length; i++) {
//                plot.point(pointLegend, Palette.COLORS[labels[i]], y_2[i]);
//            }
//        } else {
//            plot.points(y_2, pointLegend);
//        }
//
//        plot.setTitle("tSNE-2D Projection");
//        pane.add(plot);
//
////        rp = sparseBox.isSelected() ?  RandomProjection.sparse(data[0].length, 3) : RandomProjection.of(data[0].length, 3);
////        System.out.format("%d x %d Random Projection:\n", data[0].length, 3);
////        projection = rp.getProjection();
////        for (int i = 0; i < projection.nrows(); i++) {
////            for (int j = 0; j < projection.ncols(); j++) {
////                System.out.format("% .4f ", projection.get(i, j));
////            }
////            System.out.println();
////        }
////        y = rp.project(data);
//        
//        tsne =new TSNE(data, 3);
//        y_2=tsne.coordinates;
//        
//
//        
//        plot = new PlotCanvas(MathEx.colMin(y_2), MathEx.colMax(y_2));
//        if (names != null) {
//            plot.points(y_2, names);
//        } else if (labels != null) {
//            for (int i = 0; i < y_2.length; i++) {
//                plot.point(pointLegend, Palette.COLORS[labels[i]], y_2[i]);
//            }
//        } else {
//            plot.points(y_2, pointLegend);
//        }
//
//        plot.setTitle("tSNE-2D Projection");
//        pane.add(plot);

        return pane;
    }

    @Override
    public String toString() {
        return "Projection of Clinic Trial Data";
    }

    public static void main(String argv[]) {
        Demo demo = new Demo();
        JFrame f = new JFrame("Projection of Clinic Trial Data");
        f.setSize(new Dimension(1500, 1000));
        f.setLocationRelativeTo(null);
        f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        f.getContentPane().add(demo);
        f.setVisible(true);
    }
}
