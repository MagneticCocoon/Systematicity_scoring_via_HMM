# Systematicity-scoring-via-HMM
Calculate systematicity scores from game-logs (Json) by using HMM algorithm

## General Description
This is the 1st study in IGBL (Indicator of Game-Based Learning) project.

It is published as:
Lee, J. Y., Donkers, J., Jarodzka, H., & Van Merriënboer, J. J. (2019). How prior knowledge affects problem-solving performance in a medical simulation game: Using game-logs and eye-tracking. Computers in Human Behavior, 99, 268-277.


## Description of the project
This work was supported by the Netherlands Organization for Scientific Research (NWO) [grant numbers 055.16.117]. 
(https://www.nwo.nl/en/projects/05516117)

## How does this scoring method works?
We consider Hidden Markov Models (HMM) a suitable method to develop a score for measuring systematicity in approach, since they can be used to model hidden state transitions (i.e., phase arrangement at the unit-task level) based on a sequence of emission states (i.e., arrangement of motor reactions observed at the physical level) (Baum, Petrie, Soules, & Weiss, 1970). The probability structure resulting from fitting the HMM to participant data contains information about the level of the adherence to the ABCDE sequence in hidden states. We used this probability structure to compute our score for systematicity in ap- proach.
To do this, first, we classified the functional tasks of the GIB sce- nario into each of the ABCDE phases. Then, user-input data relevant to these functional tasks was extracted from the raw data in the game log file. The extracted data comprises the emission state sequences of ABCDE for each participant. A HMM is fitted to the sequences, resulting in a probability structure with two matrices: a state transition prob- ability matrix and an emission probability matrix. From these matrices, we calculated the HMM score by averaging the sum of the diagonal and upper co-diagonal in the state transition matrix and the diagonal sum of emission probability matrix

## The systematicity score computation via HMM
We start computing the HMM score by first extracting the ABCDE phases of the subsequent observed actions from the log file. Next, a HMM is fitted to this sequence using an EM algorithm, as provided by the R package hmm.discnp (Rabiner, 1989; Turner, 2018). The HMM is set to have 5 inner states (actual phases) and 5 emission values (ob- served actions). Since fitting an HMM using a single observed sequence is strongly dependent on the starting condition, we initialize the HMM with a transition matrix with most probability mass concentrated on the diagonal and upper co-diagonal, and an emission probability matrix with most probability mass concentrated on the diagonal.
The resulting probability structure after fitting to the observed se- quence contains information on the adherence to the ABCDE order. In the transition probability matrix, the total probability on “forbidden” transitions (e.g., jump from A to E) show how much is deviated from the order. The probability on “forbidden” emissions (e.g., an action for B in phase D) in the emission probability matrix shows how often actions are taken in a wrong phase. From this obtained probability structure, we compute a score: the total probability on legal transitions plus the total probability on legal emissions, divided by 2. This score ranges between 0 and 1.
Consequently, the HMM score increases when a performer keeps to the ABCDE phases in order, while the score decreases when the per- formance deviates from the order. For instance, in case of an ideal performer, the hidden sequence follows the ABCDE phases in a com- plete order (e.g., A-A-A-A-A-B-B-B-C-C-C-C-D-D-D-D-D-E-E-E-E-E). The HMM score for this example is 1.0. In the case of a less ideal performer, the sequence may deviate from the complete order (e.g., A-A-A-B-E-C- C-E-D-B-C-A-C-B-D-C-E-C-D-E-D-A-E-E), signifying that this performer jumped around the phases using less ideal rules. The HMM score for this example is 0.792.




