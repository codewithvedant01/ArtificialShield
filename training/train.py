import os
import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)
from datasets import load_dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def main():
    model_name = "microsoft/deberta-v3-base"
    seed = 42
    torch.manual_seed(seed)
    
    # In a real scenario, replace with actual dataset path or HF hub dataset
    # e.g., dataset = load_dataset("csv", data_files={"train": "data/train.csv", "val": "data/val.csv"})
    print("Loading dataset...")
    try:
        dataset = load_dataset("deepset/prompt-injections", split="train")
        # Split into train/val/test
        train_test = dataset.train_test_split(test_size=0.2, seed=seed)
        val_test = train_test['test'].train_test_split(test_size=0.5, seed=seed)
        
        train_dataset = train_test['train']
        val_dataset = val_test['train']
        test_dataset = val_test['test']
    except Exception as e:
        print(f"Skipping actual dataset load for skeleton code: {e}")
        return

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_val = val_dataset.map(tokenize_function, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

    training_args = TrainingArguments(
        output_dir="./models/deberta-v3-finetuned",
        eval_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
        seed=seed,
        save_total_limit=2,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        compute_metrics=compute_metrics,
    )

    print("Starting training...")
    trainer.train()
    
    print("Saving model...")
    trainer.save_model("./models/deberta-v3-finetuned-final")
    tokenizer.save_pretrained("./models/deberta-v3-finetuned-final")

if __name__ == "__main__":
    main()
