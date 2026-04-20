if __name__ == "__main__":
    print("\n🧠 LocalMind Agent — type your task, Ctrl+C to quit\n")
    while True:
        try:
            task = input("Task > ").strip()
            if task:
                print(task)
        except KeyboardInterrupt:
            print("\n bye!")
            break

