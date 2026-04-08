 code = """
    Start {
        Function add(a Number, b Number) {
            Mek result Number;
            Set result To a + b;
            Return result;
        }

        Mek x Number;
        Set x To 2;

        Set x To x + 5;

        if (x > 10) {
            Show "x is greater than 10", x;
        } Else {
            Show "x is small";
        }

        add(3, 4);
    } Done;
    """