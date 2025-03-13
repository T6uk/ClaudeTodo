gsap.defaults({
  ease: "linear",
  duration: 1
});


gsap.to("svg",{
  scale: 1.2,
  repeat: -1,
  yoyo: true,
  duration: 5,
  delay: 2,
  ease: "power1.inOut"
})

gsap.set("#smoke",{
  x:10,
  y:5
});

gsap.to("#smoke",{
  rotation: -360,
  transformOrigin: "center",
  duration: 5,
  repeat: -1
});

gsap.to("#smoke",{
  y: 10,
  duration: 5,
  repeat: -1,
  yoyo: true
});

///tail///

let tail = gsap.timeline({repeat: -1, yoyo: true,});

tail.to("#tail",{
  ease: "power1.in",
  morphSVG:{shape:"M506.637,298.528L506.637,350.214"},
  duration:0.5,
  delay:3
        })
    .to("#tail",{
  ease: "power1.out",
  morphSVG:{shape:"M506.637,298.528L506.637,323.299C506.637,323.299 506.699,350.214 534.849,350.214"}
        })


///skate//



let skate = gsap.timeline({repeat: -1, });

skate
  .to("#skateCat",{
  x:20,
  delay:4 + 0.5,
  ease: "power1.inOut"
})
  .to("#skateCat",{
  x:0,
  delay:2.5,
  ease: "power1.inOut"
});

let bump = gsap.timeline({repeat: -1});
let bumpDura = 0.2;

bump
  .to("#skate, #cat",{
  y: -2,
  delay:3,
  duration: bumpDura
},0)
  .to("#skate, #cat",{
  y: 0,
  duration: bumpDura
})
  .to("#tire-front, #tire-back",{
  y: -2,
  delay:3,
  duration: bumpDura,
  stagger:0.2
},0)
  .to("#tire-front, #tire-back",{
  y: 0,
  duration: bumpDura,
  stagger:0.2
})
 .to("#face",{
  y: -2,
  delay:3,
  duration: bumpDura,
},0.1)
  .to("#face",{
  y: 0,
  duration: bumpDura,
});

//tires//

let tires = gsap.timeline({repeat: -1});

tires.to('#tire-front, #tire-back',{
  rotation: 360,
  transformOrigin: "center",
  duration:0.5
});

//cat//

gsap.to("#left-hand",{
  rotate: -20,
  transformOrigin: "top",
  repeat: -1,
  yoyo: true,
  duration: 2,
   ease: "power1.inOut"
});


///zzz///



gsap.set('#fly',{
  x: 70,
  y: 50,
  scale: 1.4
});

gsap.to(".zzz",{
  x: "random(-80, -150)",
  y: "random(-80, -30)",
  rotation: "random(20,120)",
  duration: 3,
      repeat: -1,
  opacity: 0,
  stagger: {
      each: 1.2,
  }
})