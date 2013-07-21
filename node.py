"""
    This module represents a cluster's computational node.

    Computer Systems Architecture course
    Assignment 1 - Cluster Activity Simulation
    march 2013
"""
import threading
import thread
from threading import *

class NewThread(Thread):
 
   def __init__( self, node, row, col, block_size , matrix_type):
         Thread.__init__( self )
         self.node = node
         self.row = row
         self.col = col
         self.block_size = block_size
         self.result = 0
         self.matrix_type = matrix_type
 
   def run( self ):
        self.node.data_store.register_thread(self.node)
        i = self.row % self.block_size
        j = self.col % self.block_size
        if self.matrix_type == 'a':
            self.result = self.node.data_store.get_element_from_a(self.node, i, j)
        elif  self.matrix_type == 'b':
             self.result = self.node.data_store.get_element_from_b(self.node, i, j)

class Node:
    """
        Class that represents a cluster node with computation and storage functionalities.
    """

    def __init__(self, node_ID, block_size, matrix_size, data_store):
        """
            Constructor.

            @param node_ID: a pair of IDs uniquely identifying the node; 
            IDs are integers between 0 and matrix_size/block_size
            @param block_size: the size of the matrix blocks stored in this node's datastore
            @param matrix_size: the size of the matrix
            @param data_store: reference to the node's local data store
        """
        self.node_ID = node_ID
        self.block_size = block_size
        self.matrix_size = matrix_size
        self.data_store = data_store
        self.node_threads1 = {}
        self.node_threads2 = {}
        self.nodes = []

    def set_nodes(self, nodes):
        """
            Informs the current node of the other nodes in the cluster. 
            Guaranteed to be called before the first call to compute_matrix_block.

            @param nodes: a list containing all the nodes in the cluster
        """

        self.nodes = nodes

    def compute_matrix_block(self, start_row, start_col, num_rows, num_cols):
        """
            Computes a given block of the result matrix.
            The method invoked by FEP nodes.

            @param start_row: the index of the first row in the block
            @param start_column: the index of the first column in the block
            @param num_rows: number of rows in the block
            @param num_columns: number of columns in the block

            @return: the block of the result matrix encoded as a row-order list of lists of integers
        """
        end_row = start_row + num_rows
        end_col = start_col + num_cols

        for row in range(start_row, end_row, 1):
            for col in range(0, self.matrix_size, 1): 
                i = int(row / self.block_size)
                j = int(col / self.block_size)
                node = None
                for n in self.nodes:
                    if n.node_ID[0] == i and n.node_ID[1] == j:
                       node = n

                t1 = NewThread(node, row, col,  self.block_size, 'a')
                t1.start()
                t1.join()
                t11 = None
                self.node_threads1[(row,col)] = (t1, t11)

        for row in range(0, self.matrix_size, 1):
            for col in range(start_col, end_col, 1): 
                i = int(row / self.block_size)
                j = int(col / self.block_size)
                node = None
                for n in self.nodes:
                    if n.node_ID[0] == i and n.node_ID[1] == j:
                       node = n

                t2 = NewThread(node, row, col, self.block_size, 'b')
                t2.start()
                t2.join()
                t22 = None
                self.node_threads2[(row,col)] = (t2, t22)

        matrix=[[0 for i in range(num_cols)] for j in range(num_rows)]

        for row in range(start_row, end_row, 1):
            for col in range(start_col, end_col, 1): 
                for k in range(0, self.matrix_size, 1):
                    matrix[row-start_row][col-start_col] += self.node_threads1[(row,k)][0].result * self.node_threads2[(k,col)][0].result 
        return matrix
        pass

    def shutdown(self):
        """
            Instructs the node to shutdown (terminate all threads).
        """
	pass
