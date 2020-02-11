This is an example hello world C program.
We can define codeblocks with `---`

---hello.c---
@{Includes}

@{print function}
int main() {
    @{Print a string}
    return 0;
}
---

Now we can define the `Includes` codeblock:

---Includes---
#include <stdio.h>
---

Finally, our program needs to print "hello world"

---Print a string---
printf("hello world\n");
---

However we can nest like

---print function---
int function(){
    @{print elements}
}
---


And print elements

---print elements---
int i=0;
for (i=0; i<10; i++){
    printf("i=%i\n", i)
}
---