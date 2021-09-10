import time
import datetime

from transformers import BertForSequenceClassification, AdamW, BertConfig
from transformers import get_linear_schedule_with_warmup

import numpy as np
import random
from tqdm import trange

# Function to calculate the accuracy of our predictions vs labels
def flat_accuracy(preds, labels):
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return np.sum(pred_flat == labels_flat) / len(labels_flat)

def format_time(elapsed):
    '''
    Takes a time in seconds and returns a string hh:mm:ss
    '''
    # Round to the nearest second.
    elapsed_rounded = int(round((elapsed)))
    
    # Format as hh:mm:ss
    return str(datetime.timedelta(seconds=elapsed_rounded))

lr_options = [
    1e-7,
    5e-7
]

wd_options = [
    5e-6,
    1e-5,
    5e-5,
]

best_lr = best_wd = best_epoch_no = None
best_acc = 0

for lr in lr_options:
    for wd in wd_options:
        model = BertForSequenceClassification.from_pretrained(
            "bert-base-uncased",
            num_labels=2,
            output_attentions=False,
            output_hidden_states=False
        )

        # Running the model on GPU.
        model.cuda()

        optimizer = AdamW(
            model.parameters(),
            lr = lr,
            weight_decay = wd, # L2 Regularization
            eps = 1e-8 
        )

        epochs = 3
        total_steps = len(train_dataloader) * epochs
        scheduler = get_linear_schedule_with_warmup(optimizer, 
                                                    num_warmup_steps = 0, # Default value in run_glue.py
                                                    num_training_steps = total_steps)

        seed_val = 42

        random.seed(seed_val)
        np.random.seed(seed_val)
        torch.manual_seed(seed_val)
        torch.cuda.manual_seed_all(seed_val)

        training_stats = []

        # Measure the total training time for the whole run.
        total_t0 = time.time()

        print()
        print(f"Running training for {lr} {wd}")
        print()

        # For each epoch...
        for epoch_i in range(0, epochs):
            
            # ========================================
            #               Training
            # ========================================
            
            # Perform one full pass over the training set.

            print("")
            print('[{}  {}]: ======== Epoch {:} / {:} ========'.format(lr, wd, epoch_i + 1, epochs))
            print(f'[{lr}  {wd}]: Training...')

            t0 = time.time()

            total_train_loss = 0
            model.train()

            # For each batch of training data...
            for step, batch in enumerate(train_dataloader):

                # Progress update every 40 batches.
                if step % 40 == 0 and not step == 0:
                    # Calculate elapsed time in minutes.
                    elapsed = format_time(time.time() - t0)
                    print('[{}  {}]:   Batch {:>5,}  of  {:>5,}.    Elapsed: {:}.'.format(lr, wd, step, len(train_dataloader), elapsed))

                b_input_ids = batch[0].to(device)
                b_input_mask = batch[1].to(device)
                b_labels = batch[2].to(device)
                model.zero_grad()        

                output = model(b_input_ids, 
                            token_type_ids=None, 
                            attention_mask=b_input_mask, 
                            labels=b_labels
                )

                loss = output.loss
                total_train_loss += loss

                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

                optimizer.step()
                scheduler.step()

            # Calculate the average loss over all of the batches.
            avg_train_loss = total_train_loss / len(train_dataloader)            
            
            # Measure how long this epoch took.
            training_time = format_time(time.time() - t0)

            print()
            print(f"[{lr}  {wd} {epoch_i}]: ", end='')
            print("  Average training loss: {0:.2f}".format(avg_train_loss))
            print(f"[{lr}  {wd} {epoch_i}]: ", end='')
            print("  Training epoch took: {:}".format(training_time))
                
            # ========================================
            #               Validation
            # ========================================
            print()
            print(f"[{lr}  {wd} {epoch_i}]: ", end='')
            print("Running Validation...")

            t0 = time.time()
            model.eval()

            # Tracking variables 
            total_eval_accuracy = 0
            total_eval_loss = 0
            nb_eval_steps = 0

            for batch in validation_dataloader:

                b_input_ids = batch[0].to(device)
                b_input_mask = batch[1].to(device)
                b_labels = batch[2].to(device)
                
                with torch.no_grad():
                    output = model(
                        b_input_ids, 
                        token_type_ids=None, 
                        attention_mask=b_input_mask,
                        labels=b_labels
                    )
                    
                # Accumulate the validation loss.
                loss = output.loss
                logits = output.logits
                total_eval_loss += loss
                
                label_ids = b_labels.cpu().numpy()
                logits = logits.detach().cpu().numpy()
                total_eval_accuracy += flat_accuracy(logits, label_ids)

            # Report the final accuracy for this validation run.
            avg_val_accuracy = total_eval_accuracy / len(validation_dataloader)
            print(f"[{lr}  {wd} {epoch_i}]: ", end='')
            print("  Accuracy: {0:.2f}".format(avg_val_accuracy))

            if (avg_val_accuracy > best_acc):
                best_acc = avg_val_accuracy
                best_lr = lr
                best_wd = wd
                best_epoch_no = epoch_i

            # Calculate the average loss over all of the batches.
            avg_val_loss = total_eval_loss / len(validation_dataloader)
            
            # Measure how long the validation run took.
            validation_time = format_time(time.time() - t0)
            
            print(f"[{lr}  {wd} {epoch_i}]: Validation Loss: {avg_val_loss}")
            print(f"[{lr}  {wd} {epoch_i}]: ", end='')
            print("Validation took: {:}".format(validation_time))

            # Record all statistics from this epoch.
            training_stats.append(
                {
                    'epoch': epoch_i + 1,
                    'Training Loss': avg_train_loss,
                    'Valid. Loss': avg_val_loss,
                    'Valid. Accur.': avg_val_accuracy,
                    'Training Time': training_time,
                    'Validation Time': validation_time
                }
            )

            print(f"[{lr}  {wd}  {epoch_i}]: {best_acc} {best_lr} {best_wd}")

        print()
        print(f"[{lr}  {wd}]: Training complete!")

        print("Total training took {:} (h:mm:ss)".format(format_time(time.time()-total_t0)))