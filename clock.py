from apscheduler.schedulers.blocking import BlockingScheduler
from utils import scrape, clean_data, process_data
import pickle

sched = BlockingScheduler()


@sched.scheduled_job("cron", day_of_week="mon-sun", hour=3)
def scheduled_job():
    print("This job is run every day at 03:00 UTC")
    conferences = ["#NLProc", "#acl2020nlp", "#EMNLP2020", "#EACL2021", "#COLING2020"]
    for name in conferences:
        save = dict()
        all_tweets = scrape(name, 1)
        data_df = clean_data(name, all_tweets)
        save["name"] = name[1:] if name!="#acl2020nlp" else "ACL2020"
        process_data(data_df, save)
        pickle.dump(save, f"./data/processed_{name}.pkl", -1)


sched.start()
