while (<STDIN>) {
        if (m|\((.+)\) = ([\da-z]{32})| ) {
                print "$1|$2\n";
        }
}
