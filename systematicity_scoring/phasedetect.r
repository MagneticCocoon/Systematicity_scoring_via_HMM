
library(hmm.discnp)
library(ggplot2)

# parameter free HMM training from discrete data


trainhmm <- function(y) {
  m <- diag(5)  # create a "dirty" matrix as a start point for the learning. No zeros or ones.
  m[,]<-0.01
  diag(m) = 0.96
  yval <- c(1,2,3,4,5)  
  h <- hmm(y,yval, par0 = list(tpm=m, Rho=m), K=5, stationary=FALSE, cis=FALSE, newstyle=FALSE)
  return(h)
}

seqprob <- function(hmm,y) {
  # compute (kind of) probability of generating sequence y by hmm
  # first apply viterbi to attain most probable states
  s   <- viterbi(y,Rho=hmm$Rho, tpm=hmm$tpm, ispd = c(0.96,0.01,0.01,0.01,0.01))
  # then compute probability of output given these states
  prs <- pr(s,y,Rho=hmm$Rho, tpm=hmm$tpm, ispd = c(0.96,0.01,0.01,0.01,0.01))
  return(list(s=s, p=prs))
}

score.hmm <- function(hmm) {
  result <- list(log.like = hmm$log.like)
  result$tpm.score = (sum(diag(hmm$tpm)) + sum(diag(hmm$tpm[,-1])))/5  # our measure for how close to the ideal (= all 1 diag)
  result$Rho.score = sum(diag(hmm$Rho))/5  # our measure for how close to the ideal (= all 1 diag)
  result$seq.prob = seqprob(hmm, hmm$y)
  result$score = (result$tpm.score + result$Rho.score + result$seq.prob$p) / 3
  class(result) = "hmm.score"
  return(result)
} 

#  real data....


source("realseq.1.r")

res <- lapply(phasedata, function(y) {
    h <- trainhmm(y$seq)
    sc <- score.hmm(h)
    r <- list(level = y$type,
              id = y$id,
              tpmsc = sc$tpm.score,
              rhosc = sc$Rho.score,
              pr = sc$seq.prob$p,
              loglike = sc$log.like,
              len = length(h$y)
              )
    return(data.frame(r))
})

dfres <- do.call(rbind,res)
rm(res)

dfres$score = (dfres$tpmsc + dfres$rhosc)/2

# remove outlier
data <- dfres[(dfres$level == "X") & (dfres$score>0.6) | (dfres$level == "N") & (dfres$score>0.55),]
dfres <- dfres[(dfres$level == "X") & (dfres$score>0.6) | (dfres$level == "N") & (dfres$score>0.55),]

# outliers in tpm- and rhoscore; do not remove these AND the ones in score at same time!
# same guy is outlier in both tpm and rhosc (id 19)
#dfres <- dfres[(dfres$level == "X") | (dfres$level == "N") & (dfres$rhosc>0.40),]


data <- dfres

ggplot(dfres, aes(tpmsc, colour=level)) + 
  geom_histogram(aes(y =..density..,fill=level),  alpha = .2, bins=15) + 
  geom_density() + ggtitle("Distribtion of TPM score")

ggplot(dfres, aes(rhosc, colour=level)) + 
  geom_histogram(aes(y =..density..,fill=level),  alpha = .2, bins=15) + 
  geom_density() + ggtitle("Distribtion of Rho score")

ggplot(dfres, aes(score, colour=level)) + 
  geom_histogram(aes(y =..density..,fill=level),  alpha = .2, bins=15) + 
  geom_density() + ggtitle("Distribtion of score")

ggplot(dfres, aes(pr, colour=level)) + 
  geom_histogram(aes(y =..density..,fill=level),  alpha = .2, bins=15) + 
  geom_density() + ggtitle("Distribtion of seq.prob")

ggplot(dfres, aes(len, colour=level)) + 
  geom_histogram(aes(y =..density..,fill=level),  alpha = .2, bins=15) + 
  geom_density() + ggtitle("Distribtion of seq.len")

X <- dfres[(dfres$level == "X"),]
N <- dfres[(dfres$level == "N"),]
ggqqplot(X$score) + ggtitle("QQ-Plot of Score (X)")
shapiro.test(X$score)

ggqqplot(N$score) + ggtitle("QQ-Plot of Score (N)")
shapiro.test(N$score)
# seqlen
ggqqplot(X$len) + ggtitle("QQ-Plot of Seq.len (X)")
shapiro.test(X$len)
ggqqplot(N$len) + ggtitle("QQ-Plot of Seq.len (N)")
shapiro.test(N$len)

ggplot(dfres, aes(level, len)) +
  geom_boxplot() +
  ggtitle("Boxplot of Seq.len per level")

shapiro.test(X$tpm)
shapiro.test(N$tpm)

shapiro.test(X$rhosc)
shapiro.test(N$rhosc)

# statistical analysis using compareGroups
library(compareGroups)

res <- compareGroups(level ~ . -id, data=data)
print(res)

plot(res[1], bivar=TRUE)
plot(res[2], bivar=TRUE)
plot(res[6], bivar=TRUE)

summary(res[6])

restab <- createTable(res)
print(restab)


# compute effect size (Cohen's d)
library(effsize)

cohen.d(formula=tpmsc ~level, data=data)
cohen.d(formula=rhosc ~level, data=data)
cohen.d(formula=score ~level, data=data)  # large effect!
cohen.d(formula=len ~level, data=data)

# compute t-test for same data

t.test(tpmsc ~level, data=data)
t.test(rhosc ~level, data=data)
t.test(score ~level, data=data)
t.test(len ~level, data=data)
