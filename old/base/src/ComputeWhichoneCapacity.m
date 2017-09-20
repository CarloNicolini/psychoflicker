function [CapacityVsNumTargets, AsymptoteEstimate] = ComputeWhichoneCapacity(numItems, numTargets, percentCorrect, show, simulate)%% function [CapacityVsNumTargets, AsymptoteEstimate] = ComputeWhichoneCapacity(numItems, numTargets, percentCorrect, show, simulate)% George Alvarez: alvarez@mit.edu% Version: 1.0% Last Modified: 10.17.2005 % Demo: [CapacityVsNumTargets, AsymptoteEstimate] = ComputeWhichoneCapacity(10, [1 2 3 4], [100 100 90 80], 1, 0)% ********** Input Variables% numItems: total number of items on the screen% numTargets: an array with the number of targets items% percentCorrect: percent correct for each number of targets% show: whether or not to plot the results% simulate: whether or not to run monte carlo simulations% **********  % ********** Return Values% CapacityVsNumTargets: capacity as a function of the number of targets% Asymptote: the asymptotic capacity estimate% ********** % ********** Purpose (what this function does)% This function computes a capacity estimate from accuracy in the tracking% task when subjects have to decide which of two highlighted items is the% target item.% ********** % ********** Logic of Capacity Calculation% % C = N*(2*P-1)     (1)% where C = capacity, P = proportion correct, N = number of target items.%% The logic is that when two items are highlighted (one target, one% distractor), the subject will know which one is the distractor on C/N% percent of the trials. On the other trials (N-C)/N, the subject guesses% with 50% accuracy (chance).%% In general%% P = C/N * 1 + (N-C)/N * .5    (2)% % solve for C, and you get equation (1).% % ********** % ********** Outline% This function is broken down into 2 main steps% 1. initialize some variables% 2. compute capacity% 3. plot the results% 4. run monte carlso simulation% ********** % 1. Initialize Some Variables ********************************************% we want to work with proportions (0-1)if (max(percentCorrect)>1)    percentCorrect=percentCorrect./100;end% *************************************************************************% 2. Compute Capacity Estimate ********************************************% compute capacityCapacityVsNumTargets=numTargets.*(2*percentCorrect-1);CapacityVsNumTargets(find(CapacityVsNumTargets < 0))=0;% estimate the asymptote of this functiontempCapacity=CapacityVsNumTargets;tempNumTargets=numTargets;AsymptoteEstimate=mean(tempCapacity);while (AsymptoteEstimate >= tempNumTargets(1) & length(tempNumTargets)>1)    tempCapacity(1)=[];    tempNumTargets(1)=[];    AsymptoteEstimate=mean(tempCapacity);end% *************************************************************************% 3. Plot the Results ***************************************************** if (show)    repAsymptoteEstimate=repmat(AsymptoteEstimate,1,length(numTargets));    figure(1);    plot(numTargets,CapacityVsNumTargets,'ko-', numTargets, repAsymptoteEstimate, 'r--');    axis([0 numTargets(end)+1 0 numTargets(end)+1]);    axis('equal');    ylabel('Capacity (objects)');    xlabel('Number of Targets');    text((numTargets(end)-numTargets(1))/2,AsymptoteEstimate+.5,['Asymptote Estimate = ' num2str(AsymptoteEstimate)]);end% *************************************************************************% 4. Run Monte Carlso Simulations  ****************************************if (simulate)    for i=1:10000          % simulate 10000 trials        simItems    =10;                % sim numitems        simTargets  =4;                 % sim numtargets        simTracked  =3;                 % sim num tracked                isTarget(1:simItems)=0;         % which are targets (none at first)        isTarget(1:simTargets)=1;       % make first ones targets up to numTargets                isTracked(1:simItems)=0;        isTracked(1:simTracked)=1;                isSelected=randperm(simTargets); % which target is selected        isSelected=isSelected(1,1);                       if (isTracked(isSelected)==1)            simAccuracy(i)=1;        else            randValue=randperm(100);            randValue=randValue(1,1);            if (randValue <= 50)                simAccuracy(i)=1;            else                simAccuracy(i)=0;            end        end    end    montePercentCorrect=mean(simAccuracy)*100    monteCapacity=simTargets*(2*mean(simAccuracy)-1)    end