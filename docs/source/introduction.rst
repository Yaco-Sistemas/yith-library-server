Introduction
============

Yith Library is a web password manager. A password manager is a software that
helps you keep track of all your passwords you need in your physical and
online lives. Many people use just one password for all their different
accounts but this is a very bad idea since if one of those accounts is
compromised and the password is revealed, your whole identity is in danger.

There are several password managers that work as native desktop applications
but nowadays people tend to use many different devices in the same day:
smartphones, tablets, laptops, smart tvs are just some examples. Because of
this reason Yith Library is designed to work on the only platform that
is common to all these devices: the web. This way the user can access his
passwords no matter what device he is using.

Goals
-----

- **Openess**: Yith Library is free software. Its code is distributed under
  the terms of the AGPLv3. It is also open in the sense that it promotes
  the creation of different clients to access the passwords storage.

- **Security**: how useful is a password manager if the passwords are ever
  leaked? Yith Library takes security very seriously: user authentication
  is delegated to well known identity providers, passwords are stored
  ciphered using strong cryptography techniques, everything is served over
  the SSL/TLS protocol. These are just examples but as everything is open
  source, the best security feature is that everybody can audit the code
  and point to the weak points so fixes are applied fast.

- **Fair play**: the user should always be in control of their data,
  which is passwords in this case. He should be able to choose how
  he wants to authenticate with the server and which client he wants to use.
  But he also can decide when to close his account and remove all his data,
  get his data back from the server or simply allow or deny the use of
  web statistics about his accesses.

- **Learn**: Yith Library started as a learning experiment and its authors
  still learn a lot of things in their everyday hacking activities. They don't
  care if there are easy shortcuts for things that should be done in a
  different, more difficult way. We enjoy learning these techniques and
  we don't compromise in such cases.

- **Fun**: at the end of the day, the authors of the Yith Library, do it
  just for fun. They have boring day jobs to pay their bills so they don't
  have deadlines or pressure when they hack on Yith Library.

Architecture
------------
