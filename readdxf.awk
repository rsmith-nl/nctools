BEGIN { scale=0.28346*5; ent=0; line=0; arc=0; readl=0; arc=0; reada=0;
minx = 100000; miny = 100000; maxx = 0; maxy = 0;
print "%!PS-Adobe-2.0"; 
print "%%BoundingBox: atend"
print ".1 setlinewidth";}
/^ENTITIES/ {ent=1;}
/^ENDSEC/ {if (ent==1) ent=0;}
/^LINE/ {if (ent==1) {line=1; readl=0;}}
/^ARC/ {if (ent==1) {arc=1; reada=0;}}
/^ 10/ {if (line==1) {readl=1;} if (arc==1) {reada=1;}}
/^ 20/ {if (line==1) {readl=2;} if (arc==1) {reada=2;}}
/^ 11/ {if (line==1) readl=3;}
/^ 21/ {if (line==1) readl=4;}
/^ 40/ {if (arc==1) reada=3;}
/^ 50/ {if (arc==1) reada=4;}
/^ 51/ {if (arc==1) reada=5;}

/[0-9]*[.][0-9]+/ {
	if (readl==1) {x1=$1*scale; readl=0;}
	if (reada==1) {x1=$1*scale; reada=0;}
	if (readl==2) {y1=$1*scale; 
		printf("%f %f moveto\n", x1, y1); readl=0;
		if (x1<minx) minx = x1; if (y1<miny) miny = y1;
		if (x1>maxx) maxx = x1; if (y1>maxy) maxy = y1;
	}
	if (reada==2) {x2=$1*scale; reada=0;}
	if (readl==3) {x2=$1*scale; readl=0;}
	if (reada==3) {r=$1*scale; reada=0;}
	if (readl==4) {y2=$1*scale; printf("%f %f lineto stroke\n", x2, y2); 
		line=0; readl=0;
		if (x2<minx) minx = x2; if (y2<miny) miny = y2;
		if (x2>maxx) maxx = x2; if (y2>maxy) maxy = y2;
	}
	if (reada==4) {a1=$1; reada=0;}
	if (reada==5) {a2=$1; reada=0; arc=0;
		printf("%f %f %f %f %f arc stroke\n", x1, x2, r, a1, a2);}
}
END {
	print "showpage";
	printf("%%%%BoundingBox: %d %d %d %d\n", minx, miny, maxx, maxy);;
}
 