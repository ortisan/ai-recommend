if __name__ == "__main__":
    container = CmdContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    main()
